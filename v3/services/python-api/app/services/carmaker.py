import socket
import threading
from dataclasses import dataclass, field

from app.schemas.carmaker import ConnectionStatus, TelemetryData, build_telemetry

ESSENTIAL_QUANTITIES = [
    "Time",
    "DM.Gas",
    "DM.Brake",
    "DM.Steer.Ang",
    "DM.GearNo",
    "Car.v",
    "Vhcl.YawRate",
    "Vhcl.Steer.Ang",
    "Vhcl.sRoad",
    "Vhcl.tRoad",
    "DM.v.Trgt",
    "DM.LaneOffset",
    "Car.tx",
    "Car.ty",
    "LongCtrl.AEB.IsActive",
]

TRAFFIC_OBJECT_QUANTITIES = [
    "tx",
    "ty",
    "v_0.x",
    "v_0.y",
    "LongVel",
    "sRoad",
    "tRoad",
]


class CarMakerClient:
    def __init__(self, host: str = "localhost", port: int = 16660) -> None:
        self.host = host
        self.port = port
        self.socket: socket.socket | None = None
        self.connected = False
        self.lock = threading.Lock()

    def connect(self) -> None:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(2.0)
            self.socket.connect((self.host, self.port))
            self.connected = True
        except Exception as exc:
            self.socket = None
            self.connected = False
            raise RuntimeError(str(exc)) from exc

    def disconnect(self) -> None:
        if self.socket:
            try:
                self.socket.close()
            except OSError:
                pass
        self.socket = None
        self.connected = False

    def send_command(self, command: str, timeout: float = 2.0) -> str:
        if not self.connected or not self.socket:
            raise RuntimeError("Not connected to CarMaker")

        with self.lock:
            try:
                self.socket.settimeout(timeout)
                self.socket.sendall(f"{command}\n".encode("utf-8"))
                response = self.socket.recv(32768)
            except socket.timeout as exc:
                raise RuntimeError("No response from CarMaker (timeout)") from exc
            except OSError as exc:
                self.disconnect()
                raise RuntimeError(f"CarMaker socket error: {exc}") from exc

        if not response:
            self.disconnect()
            raise RuntimeError("Connection closed by CarMaker")

        return response.decode("utf-8", errors="replace").strip()

    def read_values_batch(self, quantities: list[str], timeout: float = 2.0) -> dict[str, float]:
        if not quantities:
            return {}

        response = self.send_command(f"DVARead {' '.join(quantities)}", timeout=timeout)
        results: dict[str, float] = {}
        if not response.startswith("O"):
            return results

        values = response[1:].strip().split()
        for quantity, raw_value in zip(quantities, values):
            try:
                results[quantity] = float(raw_value)
            except ValueError:
                continue
        return results

    def read_telemetry(self, watched_objects: list[int]) -> TelemetryData:
        raw_data = self.read_values_batch(
            ESSENTIAL_QUANTITIES + ["Traffic.nObjs"],
            timeout=1.0,
        )

        traffic_vars: list[str] = []
        for index in watched_objects:
            if index < 0:
                continue
            object_name = f"T{index:02d}"
            for quantity in TRAFFIC_OBJECT_QUANTITIES:
                traffic_vars.append(f"Traffic.{object_name}.{quantity}")

        if traffic_vars:
            raw_data.update(self.read_values_batch(traffic_vars, timeout=2.0))

        return build_telemetry(raw_data)

    def execute_command(self, command: str) -> str:
        cleaned = command.strip()
        if not cleaned:
            raise RuntimeError("Empty command")

        response = self.send_command(cleaned)
        if response.startswith("E"):
            raise RuntimeError(f"CarMaker error: {response}")
        return response or "OK (no response)"


@dataclass
class CarMakerRuntimeState:
    client: CarMakerClient | None = None
    status: ConnectionStatus = field(
        default_factory=lambda: ConnectionStatus(
            connected=False,
            host="localhost",
            port=16660,
            last_error=None,
        )
    )
    latest_telemetry: TelemetryData | None = None
    watched_objects: set[int] = field(default_factory=set)
    monitoring_active: bool = False


class CarMakerService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._state = CarMakerRuntimeState()

    def connect(self, host: str, port: int) -> ConnectionStatus:
        with self._lock:
            if self._state.client is not None:
                self._state.client.disconnect()
                self._state.client = None

            client = CarMakerClient(host=host, port=port)
            try:
                client.connect()
            except RuntimeError as exc:
                self._state.client = None
                self._state.status = ConnectionStatus(
                    connected=False,
                    host=host,
                    port=port,
                    last_error=str(exc),
                )
                raise

            self._state.client = client
            self._state.latest_telemetry = None
            self._state.status = ConnectionStatus(
                connected=True,
                host=host,
                port=port,
                last_error=None,
            )
            return self._state.status

    def disconnect(self) -> ConnectionStatus:
        with self._lock:
            if self._state.client is not None:
                self._state.client.disconnect()
            self._state.client = None
            self._state.latest_telemetry = None
            self._state.monitoring_active = False
            self._state.status = ConnectionStatus(
                connected=False,
                host=self._state.status.host,
                port=self._state.status.port,
                last_error=None,
            )
            return self._state.status

    def get_status(self) -> ConnectionStatus:
        with self._lock:
            self._sync_status()
            return self._state.status

    def get_telemetry(self) -> TelemetryData:
        with self._lock:
            client = self._require_client()
            try:
                telemetry = client.read_telemetry(sorted(self._state.watched_objects))
            except RuntimeError as exc:
                self._handle_client_error(str(exc))
                raise

            self._state.latest_telemetry = telemetry
            self._sync_status()
            self._state.status.last_error = None
            return telemetry

    def execute_command(self, command: str) -> str:
        with self._lock:
            client = self._require_client()
            try:
                result = client.execute_command(command)
            except RuntimeError as exc:
                self._handle_client_error(str(exc))
                raise

            self._sync_status()
            self._state.status.last_error = None
            return result

    def is_monitoring_active(self) -> bool:
        with self._lock:
            return self._state.monitoring_active

    def set_monitoring_state(self, active: bool) -> bool:
        with self._lock:
            self._state.monitoring_active = active
            return self._state.monitoring_active

    def set_gas(self, value: float, duration: int | None = None) -> str:
        return self._write_driver_model_value("DM.Gas", value, duration)

    def set_brake(self, value: float, duration: int | None = None) -> str:
        return self._write_driver_model_value("DM.Brake", value, duration)

    def set_steer(self, value: float, duration: int | None = None) -> str:
        return self._write_driver_model_value("DM.Steer.Ang", value, duration)

    def set_target_speed(self, speed_kmh: float) -> str:
        speed_ms = speed_kmh / 3.6
        return self._write_driver_model_value("DM.v.Trgt", speed_ms, None)

    def start_simulation(self) -> str:
        return self.execute_command("StartSim")

    def stop_simulation(self) -> str:
        return self.execute_command("StopSim")

    def get_watched_objects(self) -> list[int]:
        with self._lock:
            return sorted(self._state.watched_objects)

    def add_watched_object(self, index: int) -> list[int]:
        if index < 0:
            raise RuntimeError("Traffic object index must be non-negative")
        with self._lock:
            self._state.watched_objects.add(index)
            return sorted(self._state.watched_objects)

    def remove_watched_object(self, index: int) -> list[int]:
        with self._lock:
            self._state.watched_objects.discard(index)
            return sorted(self._state.watched_objects)

    def clear_watched_objects(self) -> list[int]:
        with self._lock:
            self._state.watched_objects.clear()
            return []

    def _write_driver_model_value(
        self,
        quantity: str,
        value: float,
        duration: int | None,
        mode: str = "Abs",
    ) -> str:
        duration_value = duration if duration is not None else 2000
        command = f"DVAWrite {quantity} {value:.4f} {duration_value} {mode}"
        return self.execute_command(command)

    def _sync_status(self) -> None:
        client_connected = self._state.client.connected if self._state.client else False
        self._state.status.connected = client_connected
        if not client_connected and self._state.client is None:
            self._state.monitoring_active = False

    def _handle_client_error(self, message: str) -> None:
        if self._state.client is None or not self._state.client.connected:
            self._state.client = None
            self._state.status.connected = False
            self._state.monitoring_active = False
        self._state.status.last_error = message

    def _require_client(self) -> CarMakerClient:
        self._sync_status()
        if self._state.client is None or not self._state.status.connected:
            raise RuntimeError("Not connected to CarMaker")
        return self._state.client


_service = CarMakerService()


def get_carmaker_service() -> CarMakerService:
    return _service
