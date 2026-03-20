from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.schemas.triggers import CreateTriggerRequest, Trigger, UpdateTriggerRequest
from app.services.triggers import TriggerService, get_trigger_service

router = APIRouter()


class TriggerHealthResponse(BaseModel):
    status: str = "ok"
    service: str = "triggers"


class MonitoringStateRequest(BaseModel):
    active: bool


@router.get("/health", response_model=TriggerHealthResponse)
async def triggers_health() -> TriggerHealthResponse:
    return TriggerHealthResponse()


@router.get("/monitoring", response_model=bool)
def is_monitoring_active(
    service: TriggerService = Depends(get_trigger_service),
) -> bool:
    return service.is_monitoring_active()


@router.post("/monitoring", response_model=bool)
def set_monitoring_state(
    request: MonitoringStateRequest,
    service: TriggerService = Depends(get_trigger_service),
) -> bool:
    return service.set_monitoring_state(request.active)


@router.get("/logs", response_model=list[str])
def get_trigger_logs(
    service: TriggerService = Depends(get_trigger_service),
) -> list[str]:
    return service.get_logs()


@router.delete("/logs", response_model=list[str])
def clear_trigger_logs(
    service: TriggerService = Depends(get_trigger_service),
) -> list[str]:
    return service.clear_logs()


@router.get("", response_model=list[Trigger])
def get_triggers(
    service: TriggerService = Depends(get_trigger_service),
) -> list[Trigger]:
    return service.list_triggers()


@router.get("/{trigger_id}", response_model=Trigger)
def get_trigger(
    trigger_id: int,
    service: TriggerService = Depends(get_trigger_service),
) -> Trigger:
    trigger = service.get_trigger(trigger_id)
    if trigger is None:
        raise HTTPException(status_code=404, detail=f"Trigger with id {trigger_id} not found")
    return trigger


@router.post("", response_model=Trigger)
def create_trigger(
    request: CreateTriggerRequest,
    service: TriggerService = Depends(get_trigger_service),
) -> Trigger:
    return service.create_trigger(request)


@router.put("/{trigger_id}", response_model=Trigger)
def update_trigger(
    trigger_id: int,
    request: UpdateTriggerRequest,
    service: TriggerService = Depends(get_trigger_service),
) -> Trigger:
    try:
        return service.update_trigger(trigger_id, request)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{trigger_id}", response_model=dict[str, bool])
def delete_trigger(
    trigger_id: int,
    service: TriggerService = Depends(get_trigger_service),
) -> dict[str, bool]:
    try:
        service.delete_trigger(trigger_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"ok": True}


@router.post("/{trigger_id}/toggle", response_model=Trigger)
def toggle_trigger(
    trigger_id: int,
    service: TriggerService = Depends(get_trigger_service),
) -> Trigger:
    try:
        return service.toggle_trigger(trigger_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{trigger_id}/toggle-rule-control", response_model=Trigger)
def toggle_rule_control(
    trigger_id: int,
    service: TriggerService = Depends(get_trigger_service),
) -> Trigger:
    try:
        return service.toggle_rule_control(trigger_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
