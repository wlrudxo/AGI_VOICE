import asyncio
import threading
import time
from collections.abc import Callable

from app.schemas.triggers import Trigger, TriggerChatEvent, utc_now
from app.services.action_service import ActionService, get_action_service
from app.services.carmaker import CarMakerService, get_carmaker_service
from app.services.chat import ChatService, get_chat_service


class TriggerExecutor:
    def __init__(
        self,
        carmaker_service: CarMakerService,
        action_service: ActionService,
        chat_service: ChatService,
    ) -> None:
        self._carmaker_service = carmaker_service
        self._action_service = action_service
        self._chat_service = chat_service

    def execute(
        self,
        trigger: Trigger,
        vehicle_data: dict[str, float],
        cancel_event: threading.Event,
        is_monitoring_active: Callable[[], bool],
        set_monitoring_state: Callable[[bool, bool], bool],
        add_log: Callable[[str], None],
        add_event: Callable[[TriggerChatEvent], None],
    ) -> None:
        cancel_event.clear()
        was_monitoring = False
        try:
            add_log("  → Pausing simulation (time scale = 0.001x)")
            was_monitoring = is_monitoring_active()
            if was_monitoring:
                set_monitoring_state(False, False)
                add_log("  → Monitoring paused (prevent timeout in low-speed mode)")
            self._carmaker_service.execute_command("DVAWrite SC.TAccel 0.001 30000 Abs")

            if trigger.use_rule_control and trigger.debug_action.strip():
                add_log("  → Rule mode: waiting 1 second")
                self._sleep_with_cancel(1.0, cancel_event)
                add_log("  → Resuming simulation (time scale = 1.0x)")
                self._carmaker_service.execute_command("DVAWrite SC.TAccel 1.0 30000 Abs")
                add_log("  → Rule mode: executing backend rule action")
                self._action_service.execute_command_sequence(
                    trigger.debug_action,
                    cancel_event=cancel_event,
                    logger=add_log,
                )
            else:
                add_log("  → LLM mode: requesting AI response")
                llm_response = asyncio.run(
                    self._request_llm(trigger, vehicle_data, cancel_event, add_log, add_event)
                )
                add_log("  → Resuming simulation (time scale = 1.0x)")
                self._carmaker_service.execute_command("DVAWrite SC.TAccel 1.0 30000 Abs")
                if cancel_event.is_set():
                    add_log("  → Trigger execution cancelled after AI response wait")
                elif llm_response:
                    add_log("  → Parsing LLM response and executing commands")
                    self._action_service.execute_command_sequence(
                        llm_response,
                        cancel_event=cancel_event,
                        logger=add_log,
                    )
            if was_monitoring:
                set_monitoring_state(True, False)
                add_log("  → Monitoring resumed")
            add_log("  ✓ Trigger action sequence completed")
        except Exception as exc:
            add_log(f"  ✗ Trigger action failed: {exc}")
            try:
                self._carmaker_service.execute_command("DVAWrite SC.TAccel 1.0 30000 Abs")
            except Exception:
                pass
            if was_monitoring:
                try:
                    set_monitoring_state(True, False)
                    add_log("  → Monitoring resumed")
                except Exception:
                    pass
        finally:
            cancel_event.clear()

    async def _request_llm(
        self,
        trigger: Trigger,
        vehicle_data: dict[str, float],
        cancel_event: threading.Event,
        add_log: Callable[[str], None],
        add_event: Callable[[TriggerChatEvent], None],
    ) -> str | None:
        try:
            system_context = self._build_system_context(trigger, vehicle_data)
            self._add_multiline_log(
                add_log,
                f"  === LLM INPUT BEGIN ({trigger.name}) ===",
                system_context,
                f"  === LLM INPUT END ({trigger.name}) ===",
            )
            add_event(
                TriggerChatEvent(
                    id=0,
                    type="system",
                    trigger_name=trigger.name,
                    content=system_context,
                    created_at=utc_now(),
                )
            )
            llm_response = await self._chat_service.generate_trigger_response(
                system_context,
                abort_event=cancel_event,
            )
            add_log(f"  ✓ LLM response received ({len(llm_response)} chars)")
            self._add_multiline_log(
                add_log,
                f"  === LLM OUTPUT BEGIN ({trigger.name}) ===",
                llm_response,
                f"  === LLM OUTPUT END ({trigger.name}) ===",
            )
            add_event(
                TriggerChatEvent(
                    id=0,
                    type="llm_response",
                    trigger_name=trigger.name,
                    content=llm_response,
                    created_at=utc_now(),
                )
            )
            return llm_response
        except Exception as exc:
            add_log(f"  ✗ LLM request failed: {exc}")
            add_event(
                TriggerChatEvent(
                    id=0,
                    type="error",
                    trigger_name=trigger.name,
                    content=f"LLM 요청 실패: {exc}",
                    created_at=utc_now(),
                )
            )
            return None

    def _sleep_with_cancel(self, seconds: float, cancel_event: threading.Event) -> None:
        deadline = time.time() + seconds
        while time.time() < deadline:
            if cancel_event.is_set():
                raise RuntimeError("Trigger execution cancelled")
            time.sleep(0.05)

    def _build_system_context(self, trigger: Trigger, vehicle_data: dict[str, float]) -> str:
        data_snapshot = "\n".join(
            f"{key}: {value:.4f}"
            for key, value in sorted(vehicle_data.items())
        )
        return (
            "## Current Vehicle Data:\n"
            f"{data_snapshot}\n\n"
            "## Trigger Message:\n"
            f"{trigger.message}"
        )

    def _add_multiline_log(
        self,
        add_log: Callable[[str], None],
        begin: str,
        content: str,
        end: str,
    ) -> None:
        add_log(begin)
        for line in content.splitlines():
            add_log(f"    {line}")
        add_log(end)


_service = TriggerExecutor(
    get_carmaker_service(),
    get_action_service(),
    get_chat_service(),
)


def get_trigger_executor() -> TriggerExecutor:
    return _service
