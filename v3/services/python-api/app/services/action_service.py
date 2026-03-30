import math
import re
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass

from app.services.carmaker import CarMakerService, get_carmaker_service


@dataclass
class VehicleCommand:
    variable: str
    value: float
    duration: int
    mode: str


@dataclass
class WaitCommand:
    milliseconds: int


@dataclass
class WaitUntilCommand:
    condition: str
    timeout: int = 30000


@dataclass
class ActionExecutionSummary:
    total_items: int
    success_count: int
    reset_count: int


class ActionService:
    def __init__(self, carmaker_service: CarMakerService) -> None:
        self._carmaker_service = carmaker_service

    def parse_command_sequence(
        self, text: str
    ) -> list[VehicleCommand | WaitCommand | WaitUntilCommand]:
        items: list[VehicleCommand | WaitCommand | WaitUntilCommand] = []
        code_block_match = re.search(r"```(?:[\w]*)\n([\s\S]*?)\n```", text)
        command_text = code_block_match.group(1) if code_block_match else text

        for raw_line in command_text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("//"):
                continue

            wait_match = re.match(r"^wait\s*\(?(\d+)\)?$", line, re.IGNORECASE)
            if wait_match:
                items.append(WaitCommand(milliseconds=int(wait_match.group(1))))
                continue

            wait_until_match = re.match(
                r"^wait_until\s+(.+?)(?:\s+(\d+))?$", line, re.IGNORECASE
            )
            if wait_until_match:
                items.append(
                    WaitUntilCommand(
                        condition=wait_until_match.group(1).strip(),
                        timeout=int(wait_until_match.group(2) or 30000),
                    )
                )
                continue

            command_match = re.match(
                r"^\s*([A-Za-z0-9._]+)\s*=\s*([0-9.-]+)\s*\|\s*(-?\d+)(?:\s*\|\s*(AbsRamp|FacRamp|Abs|Off|Fac))?$",
                line,
                re.IGNORECASE,
            )
            if command_match:
                items.append(
                    VehicleCommand(
                        variable=command_match.group(1),
                        value=float(command_match.group(2)),
                        duration=int(command_match.group(3)),
                        mode=command_match.group(4) or "Abs",
                    )
                )
                continue

            legacy_match = re.match(r"^\s*([A-Za-z0-9._]+)\s*=\s*([0-9.-]+)\s*$", line)
            if legacy_match:
                items.append(
                    VehicleCommand(
                        variable=legacy_match.group(1),
                        value=float(legacy_match.group(2)),
                        duration=2000,
                        mode="Abs",
                    )
                )

        return items

    def execute_command_sequence(
        self,
        text: str,
        cancel_event: threading.Event | None = None,
        logger: Callable[[str], None] | None = None,
    ) -> ActionExecutionSummary:
        items = self.parse_command_sequence(text)
        pending_infinite: list[VehicleCommand] = []
        success_count = 0
        reset_count = 0

        for item in items:
            self._raise_if_cancelled(cancel_event)

            if isinstance(item, WaitCommand):
                self._log(logger, f"    ⏱ wait {item.milliseconds}ms")
                self._sleep_with_cancel(item.milliseconds / 1000.0, cancel_event)
                success_count += 1
                continue

            if isinstance(item, WaitUntilCommand):
                self._log(logger, f"    ⏳ wait_until {item.condition}")
                self._execute_wait_until(item, cancel_event, logger)
                success_count += 1
                if pending_infinite:
                    self._log(
                        logger,
                        f"    ↻ Resetting {len(pending_infinite)} infinite-duration command(s)",
                    )
                    for command in pending_infinite:
                        reset = VehicleCommand(
                            variable=command.variable,
                            value=command.value,
                            duration=1,
                            mode=command.mode,
                        )
                        self._execute_vehicle_command(reset, logger, log_prefix="    ✓ Reset")
                        reset_count += 1
                    pending_infinite.clear()
                continue

            self._execute_vehicle_command(item, logger)
            success_count += 1
            if item.duration == -1:
                pending_infinite.append(item)

            self._sleep_with_cancel(0.05, cancel_event)

        return ActionExecutionSummary(
            total_items=len(items),
            success_count=success_count,
            reset_count=reset_count,
        )

    def reset_controls(self) -> tuple[int, int]:
        commands = [
            VehicleCommand("SC.TAccel", 1.0, 30000, "Abs"),
            VehicleCommand("DM.Gas", 0.0, 1, "Abs"),
            VehicleCommand("DM.Brake", 0.0, 1, "Abs"),
            VehicleCommand("DM.Steer.Ang", 0.0, 1, "Abs"),
            VehicleCommand("DM.v.Trgt", 0.0, 1, "Abs"),
            VehicleCommand("DM.LaneOffset", 0.0, 1, "Abs"),
        ]
        succeeded = 0
        for command in commands:
            self._execute_vehicle_command(command)
            succeeded += 1
        return len(commands), succeeded

    def _execute_vehicle_command(
        self,
        command: VehicleCommand,
        logger: Callable[[str], None] | None = None,
        log_prefix: str = "    ✓",
    ) -> None:
        actual_duration = 99999 if command.duration == -1 else command.duration
        raw_command = (
            f"DVAWrite {command.variable} {command.value} {actual_duration} {command.mode}"
        )
        self._carmaker_service.execute_command(raw_command)
        duration_label = "99999ms (infinite)" if command.duration == -1 else f"{command.duration}ms"
        self._log(
            logger,
            f"{log_prefix} {command.variable} = {command.value} | {duration_label} | {command.mode}",
        )

    def _execute_wait_until(
        self,
        wait_command: WaitUntilCommand,
        cancel_event: threading.Event | None = None,
        logger: Callable[[str], None] | None = None,
    ) -> None:
        parsed = self._parse_simple_condition(wait_command.condition)
        if parsed is None:
            raise RuntimeError(f"Invalid wait_until condition: {wait_command.condition}")

        start_time = time.time()
        iteration = 0
        while True:
            self._raise_if_cancelled(cancel_event)
            elapsed_ms = int((time.time() - start_time) * 1000)
            if elapsed_ms > wait_command.timeout:
                raise RuntimeError(f"Timeout after {wait_command.timeout}ms: {wait_command.condition}")

            telemetry = self._carmaker_service.get_telemetry()
            vehicle_data = telemetry.raw_data
            current_value = vehicle_data.get(parsed["variable"])

            if iteration % 10 == 0 and current_value is not None:
                self._log(
                    logger,
                    f"    → {parsed['variable']} = {current_value:.4f} (checking {parsed['operator']} {parsed['value']})",
                )

            if current_value is not None and self._evaluate_simple_condition(parsed, current_value):
                self._log(logger, f"    ✓ Condition met: {parsed['variable']} = {current_value:.4f}")
                return

            iteration += 1
            self._sleep_with_cancel(0.1, cancel_event)

    def _parse_simple_condition(self, condition: str) -> dict[str, str] | None:
        match = re.match(
            r"^\s*([A-Za-z0-9._]+)\s*(>=|<=|==|!=|>|<)\s*([0-9.-]+)\s*$",
            condition,
        )
        if not match:
            return None

        return {
            "variable": match.group(1),
            "operator": match.group(2),
            "value": match.group(3),
        }

    def _evaluate_simple_condition(self, condition: dict[str, str], actual_value: float) -> bool:
        expected = float(condition["value"])
        operator = condition["operator"]

        if operator == ">":
            return actual_value > expected
        if operator == "<":
            return actual_value < expected
        if operator == ">=":
            return actual_value >= expected
        if operator == "<=":
            return actual_value <= expected
        if operator == "==":
            return math.isclose(actual_value, expected, abs_tol=1e-4)
        if operator == "!=":
            return not math.isclose(actual_value, expected, abs_tol=1e-4)
        return False

    def _raise_if_cancelled(self, cancel_event: threading.Event | None) -> None:
        if cancel_event is not None and cancel_event.is_set():
            raise RuntimeError("Trigger execution cancelled")

    def _sleep_with_cancel(
        self,
        seconds: float,
        cancel_event: threading.Event | None = None,
    ) -> None:
        deadline = time.time() + seconds
        while time.time() < deadline:
            self._raise_if_cancelled(cancel_event)
            time.sleep(0.05)

    def _log(self, logger: Callable[[str], None] | None, message: str) -> None:
        if logger is not None:
            logger(message)


_service = ActionService(get_carmaker_service())


def get_action_service() -> ActionService:
    return _service
