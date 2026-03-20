from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.schemas.carmaker import (
    ConnectRequest,
    ConnectionStatus,
    ExecuteCommandRequest,
    MonitoringStateRequest,
    PedalControlRequest,
    TargetSpeedRequest,
    TelemetryData,
    WatchedObjectRequest,
)
from app.services.carmaker import CarMakerService, get_carmaker_service

router = APIRouter()


class CarMakerHealthResponse(BaseModel):
    status: str = "ok"
    service: str = "carmaker"


@router.get("/health", response_model=CarMakerHealthResponse)
async def carmaker_health() -> CarMakerHealthResponse:
    return CarMakerHealthResponse()


@router.post("/connect", response_model=ConnectionStatus)
def connect_carmaker(
    request: ConnectRequest,
    service: CarMakerService = Depends(get_carmaker_service),
) -> ConnectionStatus:
    try:
        return service.connect(request.host, request.port)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/disconnect", response_model=ConnectionStatus)
def disconnect_carmaker(
    service: CarMakerService = Depends(get_carmaker_service),
) -> ConnectionStatus:
    return service.disconnect()


@router.get("/status", response_model=ConnectionStatus)
def get_connection_status(
    service: CarMakerService = Depends(get_carmaker_service),
) -> ConnectionStatus:
    return service.get_status()


@router.get("/monitoring", response_model=bool)
def is_monitoring_active(
    service: CarMakerService = Depends(get_carmaker_service),
) -> bool:
    return service.is_monitoring_active()


@router.post("/monitoring", response_model=bool)
def set_monitoring_state(
    request: MonitoringStateRequest,
    service: CarMakerService = Depends(get_carmaker_service),
) -> bool:
    return service.set_monitoring_state(request.active)


@router.get("/telemetry", response_model=TelemetryData)
def get_vehicle_status(
    service: CarMakerService = Depends(get_carmaker_service),
) -> TelemetryData:
    try:
        return service.get_telemetry()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/command", response_model=str)
def execute_vehicle_command(
    request: ExecuteCommandRequest,
    service: CarMakerService = Depends(get_carmaker_service),
) -> str:
    try:
        return service.execute_command(request.command)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/control/gas", response_model=str)
def set_gas(
    request: PedalControlRequest,
    service: CarMakerService = Depends(get_carmaker_service),
) -> str:
    try:
        return service.set_gas(request.value, request.duration)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/control/brake", response_model=str)
def set_brake(
    request: PedalControlRequest,
    service: CarMakerService = Depends(get_carmaker_service),
) -> str:
    try:
        return service.set_brake(request.value, request.duration)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/control/steer", response_model=str)
def set_steer(
    request: PedalControlRequest,
    service: CarMakerService = Depends(get_carmaker_service),
) -> str:
    try:
        return service.set_steer(request.value, request.duration)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/control/target-speed", response_model=str)
def set_target_speed(
    request: TargetSpeedRequest,
    service: CarMakerService = Depends(get_carmaker_service),
) -> str:
    try:
        return service.set_target_speed(request.speed_kmh)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/simulation/start", response_model=str)
def start_simulation(
    service: CarMakerService = Depends(get_carmaker_service),
) -> str:
    try:
        return service.start_simulation()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/simulation/stop", response_model=str)
def stop_simulation(
    service: CarMakerService = Depends(get_carmaker_service),
) -> str:
    try:
        return service.stop_simulation()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/watched-objects", response_model=list[int])
def get_watched_objects(
    service: CarMakerService = Depends(get_carmaker_service),
) -> list[int]:
    return service.get_watched_objects()


@router.post("/watched-objects", response_model=list[int])
def add_watched_object(
    request: WatchedObjectRequest,
    service: CarMakerService = Depends(get_carmaker_service),
) -> list[int]:
    try:
        return service.add_watched_object(request.index)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/watched-objects/{index}", response_model=list[int])
def remove_watched_object(
    index: int,
    service: CarMakerService = Depends(get_carmaker_service),
) -> list[int]:
    return service.remove_watched_object(index)


@router.delete("/watched-objects", response_model=list[int])
def clear_watched_objects(
    service: CarMakerService = Depends(get_carmaker_service),
) -> list[int]:
    return service.clear_watched_objects()
