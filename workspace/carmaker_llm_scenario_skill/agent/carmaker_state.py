#!/usr/bin/env python3
from __future__ import annotations

import json
import socket
from dataclasses import dataclass
from urllib import error, request


STATE_LABELS = {
    -1: "preprocessing",
    -2: "idle_ready",
    -3: "postprocessing",
    -4: "model_check",
    -5: "driver_adaptation",
    -6: "fatal_error",
    -7: "waiting_for_license",
    -8: "paused",
    -10: "starting_application",
    -11: "simulink_initialization",
}


@dataclass
class DirectCarMakerStateReader:
    host: str
    port: int
    backend_url: str | None = None
    timeout_seconds: float = 2.0

    def read(self) -> dict[str, float | str | None]:
        response = self._send_command("DVARead SC.State SC.TAccel")
        if not response or not response.startswith("O"):
            if self.backend_url:
                response = self._send_backend_command("DVARead SC.State SC.TAccel")
            else:
                raise RuntimeError(f"Direct CarMaker state read failed: {response!r}")

        values = response[1:].strip().split()
        if len(values) != 2:
            if self.backend_url:
                response = self._send_backend_command("DVARead SC.State SC.TAccel")
                values = response[1:].strip().split()
            if len(values) != 2:
                raise RuntimeError(
                    "Direct CarMaker state read returned an unexpected payload: "
                    f"{response!r}"
                )

        state = float(values[0])
        time_accel = float(values[1])
        return {
            "SC.State": state,
            "SC.TAccel": time_accel,
            "SC.State.Label": interpret_sc_state(state),
            "SC.TimeMode": interpret_time_mode(state, time_accel),
        }

    def _send_command(self, command: str) -> str | None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(self.timeout_seconds)
            sock.connect((self.host, self.port))
            sock.sendall(f"{command}\n".encode("utf-8"))
            payload = sock.recv(4096)
            return payload.decode("utf-8", errors="replace").strip()
        except OSError as exc:
            raise RuntimeError(f"Direct CarMaker TCP read failed: {exc}") from exc
        finally:
            try:
                sock.close()
            except OSError:
                pass

    def _send_backend_command(self, command: str) -> str:
        if not self.backend_url:
            raise RuntimeError("Backend URL is not configured for state fallback")

        req = request.Request(
            f"{self.backend_url.rstrip('/')}/api/carmaker/command",
            data=json.dumps({"command": command}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as resp:
                body = resp.read().decode("utf-8")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Backend state read failed: HTTP {exc.code}: {detail}"
            ) from exc
        except error.URLError as exc:
            raise RuntimeError(f"Backend state read failed: {exc.reason}") from exc

        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Backend state read returned invalid JSON: {body!r}") from exc

        if not isinstance(payload, str):
            raise RuntimeError(f"Backend state read returned unexpected JSON: {payload!r}")
        return payload


def interpret_sc_state(state: float) -> str:
    state_int = int(state)
    if state_int >= 0:
        return f"running_cycle_{state_int}"
    return STATE_LABELS.get(state_int, f"unknown_{state_int}")


def interpret_time_mode(state: float, time_accel: float) -> str:
    state_int = int(state)
    if time_accel == 0.0001 and state_int >= 0:
        return "near_pause_running"
    if time_accel == 0.0001 and state_int == -8:
        return "paused_at_near_zero_taccel"
    if state_int == -8:
        return "paused"
    if state_int == -2:
        return "idle_ready"
    if state_int == -6:
        return "fatal_error"
    if state_int >= 0:
        return "running"
    return "not_running"
