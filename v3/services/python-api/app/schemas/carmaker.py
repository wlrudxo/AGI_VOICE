from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class ConnectionStatus(CamelModel):
    connected: bool
    host: str
    port: int
    last_error: str | None = None


class ConnectRequest(CamelModel):
    host: str = "localhost"
    port: int = 16660


class ExecuteCommandRequest(CamelModel):
    command: str


class MonitoringStateRequest(CamelModel):
    active: bool


class WatchedObjectRequest(CamelModel):
    index: int


class PedalControlRequest(CamelModel):
    value: float
    duration: int | None = None


class TargetSpeedRequest(CamelModel):
    speed_kmh: float


class TelemetryData(CamelModel):
    time: float | None = None
    dm_gas: float | None = None
    dm_brake: float | None = None
    dm_steer_ang: float | None = None
    dm_gear_no: float | None = None
    car_v: float | None = None
    vhcl_yaw_rate: float | None = None
    vhcl_steer_ang: float | None = None
    vhcl_s_road: float | None = None
    vhcl_t_road: float | None = None
    dm_v_trgt: float | None = None
    dm_lane_offset: float | None = None
    car_tx: float | None = None
    car_ty: float | None = None
    aeb_is_active: float | None = None
    traffic_n_objs: float | None = None
    raw_data: dict[str, float]


def build_telemetry(raw_data: dict[str, float]) -> TelemetryData:
    return TelemetryData(
        time=raw_data.get("Time"),
        dm_gas=raw_data.get("DM.Gas"),
        dm_brake=raw_data.get("DM.Brake"),
        dm_steer_ang=raw_data.get("DM.Steer.Ang"),
        dm_gear_no=raw_data.get("DM.GearNo"),
        car_v=raw_data.get("Car.v"),
        vhcl_yaw_rate=raw_data.get("Vhcl.YawRate"),
        vhcl_steer_ang=raw_data.get("Vhcl.Steer.Ang"),
        vhcl_s_road=raw_data.get("Vhcl.sRoad"),
        vhcl_t_road=raw_data.get("Vhcl.tRoad"),
        dm_v_trgt=raw_data.get("DM.v.Trgt"),
        dm_lane_offset=raw_data.get("DM.LaneOffset"),
        car_tx=raw_data.get("Car.tx"),
        car_ty=raw_data.get("Car.ty"),
        aeb_is_active=raw_data.get("LongCtrl.AEB.IsActive"),
        traffic_n_objs=raw_data.get("Traffic.nObjs"),
        raw_data=raw_data,
    )
