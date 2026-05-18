from __future__ import annotations

import json
import math
import re
import socket
from dataclasses import dataclass
from typing import Any, Protocol
from urllib import error, request


DEFAULT_BACKEND_URL = "http://127.0.0.1:8010"
DEFAULT_CARMAKER_HOST = "localhost"
DEFAULT_CARMAKER_PORT = 16660
DEFAULT_QUANTITIES = [
    "Time",
    "Car.v",
    "Car.ax",
    "Vhcl.sRoad",
    "Vhcl.tRoad",
    "DM.v.Trgt",
    "DM.Gas",
    "DM.Brake",
    "DM.Steer.Ang",
    "Traffic.nObjs",
]
STATE_QUANTITIES = ["SC.State", "SC.TAccel"]
TOKEN_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_.]*\b")


class CommandClient(Protocol):
    def command(self, command: str) -> str:
        ...


@dataclass
class BackendClient:
    base_url: str

    def _url(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}{path}"

    def get_json(self, path: str) -> Any:
        req = request.Request(self._url(path), method="GET")
        return self._read_json(req)

    def post_json(self, path: str, payload: dict[str, Any]) -> Any:
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self._url(path),
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        return self._read_json(req)

    def command(self, command: str) -> str:
        result = self.post_json("/api/carmaker/command", {"command": command})
        if not isinstance(result, str):
            raise RuntimeError(f"Unexpected command response: {result!r}")
        return result

    def _read_json(self, req: request.Request) -> Any:
        try:
            with request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode("utf-8")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"{req.method} {req.full_url} failed: {exc.code} {detail}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"{req.method} {req.full_url} failed: {exc.reason}") from exc
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return body


@dataclass
class DirectCarMakerCommandClient:
    host: str
    port: int
    timeout_seconds: float = 5.0

    def command(self, command: str) -> str:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(self.timeout_seconds)
            sock.connect((self.host, self.port))
            sock.sendall(f"{command}\n".encode("utf-8"))
            payload = sock.recv(65536)
        except OSError as exc:
            raise RuntimeError(f"Direct CarMaker command failed: {exc}") from exc
        finally:
            try:
                sock.close()
            except OSError:
                pass
        if not payload:
            raise RuntimeError("Direct CarMaker command returned no response")
        response = payload.decode("utf-8", errors="replace").strip()
        if response.startswith("E"):
            raise RuntimeError(f"CarMaker error: {response}")
        return response or "OK (no response)"


def ensure_connection(
    client: BackendClient,
    connect_if_needed: bool,
    host: str,
    port: int,
) -> dict[str, Any]:
    status = client.get_json("/api/carmaker/status")
    if status.get("connected"):
        return status
    if not connect_if_needed:
        raise RuntimeError("CarMaker is not connected. Connect first or pass --connect.")
    return client.post_json("/api/carmaker/connect", {"host": host, "port": port})


def create_command_client(args: Any) -> CommandClient:
    if args.direct_carmaker:
        if not getattr(args, "quiet", False):
            print(f"Connected directly to CarMaker: {args.host}:{args.port}", flush=True)
        return DirectCarMakerCommandClient(args.host, args.port)
    client = BackendClient(args.backend_url)
    status = ensure_connection(client, args.connect, args.host, args.port)
    if not getattr(args, "quiet", False):
        print(f"Connected to CarMaker via backend: {status['host']}:{status['port']}", flush=True)
    return client


def parse_quantity_arg(text: str | None) -> list[str]:
    if not text:
        return list(DEFAULT_QUANTITIES)
    quantities = [part.strip() for part in text.split(",") if part.strip()]
    if not quantities:
        raise RuntimeError("Quantity list is empty")
    return quantities


def parse_dvaread_response(response: str, quantities: list[str]) -> dict[str, float]:
    if not response.startswith("O"):
        raise RuntimeError(f"DVARead failed: {response!r}")
    values = response[1:].strip().split()
    if len(values) != len(quantities):
        raise RuntimeError(
            f"DVARead returned {len(values)} value(s) for {len(quantities)} quantity request: {response!r}"
        )
    parsed: dict[str, float] = {}
    for quantity, raw_value in zip(quantities, values):
        try:
            parsed[quantity] = float(raw_value)
        except ValueError:
            parsed[quantity] = math.nan
    return parsed


def read_quantities(client: CommandClient, quantities: list[str]) -> dict[str, float]:
    response = client.command(f"DVARead {' '.join(quantities)}")
    return parse_dvaread_response(response, quantities)


def quantities_for_expression(expression: str) -> list[str]:
    reserved = {"and", "or", "not", "abs", "sqrt", "pow", "min", "max", "True", "False"}
    quantities: list[str] = []
    for token in TOKEN_RE.findall(expression):
        if token not in reserved and token not in quantities:
            quantities.append(token)
    return quantities


def evaluate_expression(expression: str, values: dict[str, float]) -> bool:
    if not expression.strip():
        return False
    normalized = expression.replace("&&", " and ").replace("||", " or ")
    reserved = {"and", "or", "not", "abs", "sqrt", "pow", "min", "max", "True", "False"}

    def replace_token(match: re.Match[str]) -> str:
        token = match.group(0)
        if token in reserved:
            return token
        return f'_get("{token}")'

    python_expr = TOKEN_RE.sub(replace_token, normalized)
    safe_globals = {
        "__builtins__": {},
        "abs": abs,
        "sqrt": math.sqrt,
        "pow": pow,
        "min": min,
        "max": max,
    }
    safe_locals = {"_get": lambda key: values.get(key, 0.0)}
    return bool(eval(python_expr, safe_globals, safe_locals))


def strip_ok_prefix(response: str) -> str:
    return response[1:].strip() if response.startswith("O") else response
