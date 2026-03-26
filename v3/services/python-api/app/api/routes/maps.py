from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.schemas.maps import BuildResult, CreateMapRequest, EmbedResult, GetMapsQuery, MapRecord, MapSearchResult, UpdateMapRequest
from app.services.maps import MapService, get_map_service

router = APIRouter()


class MapsHealthResponse(BaseModel):
    status: str = "ok"
    service: str = "maps"


@router.get("/health", response_model=MapsHealthResponse)
async def maps_health() -> MapsHealthResponse:
    return MapsHealthResponse()


@router.post("", response_model=MapRecord)
def create_map(
    request: CreateMapRequest,
    service: MapService = Depends(get_map_service),
) -> MapRecord:
    try:
        return service.create_map(request)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[MapRecord])
def get_maps(
    category: str | None = Query(default=None),
    is_embedded: bool | None = Query(default=None),
    search: str | None = Query(default=None),
    service: MapService = Depends(get_map_service),
) -> list[MapRecord]:
    query = GetMapsQuery(category=category, is_embedded=is_embedded, search=search)
    return service.get_maps(query)


@router.get("/count", response_model=int)
def get_map_count(
    service: MapService = Depends(get_map_service),
) -> int:
    return service.get_map_count()


@router.get("/search", response_model=list[MapSearchResult])
def search_maps(
    query: str = Query(..., min_length=1),
    top_k: int = Query(default=5, ge=1, le=50),
    service: MapService = Depends(get_map_service),
) -> list[MapSearchResult]:
    try:
        return service.search_maps(query, top_k=top_k)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/embeddings/build-all", response_model=BuildResult)
def build_all_embeddings(
    rebuild: bool = Query(default=False),
    service: MapService = Depends(get_map_service),
) -> BuildResult:
    try:
        return service.build_all_embeddings(rebuild=rebuild)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/embeddings/health", response_model=str)
def embeddings_health(
    service: MapService = Depends(get_map_service),
) -> str:
    return service.embeddings_health()


@router.get("/{map_id}", response_model=MapRecord)
def get_map_by_id(
    map_id: int,
    service: MapService = Depends(get_map_service),
) -> MapRecord:
    try:
        return service.get_map_by_id(map_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{map_id}", response_model=MapRecord)
def update_map(
    map_id: int,
    request: UpdateMapRequest,
    service: MapService = Depends(get_map_service),
) -> MapRecord:
    try:
        return service.update_map(map_id, request)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{map_id}", response_model=dict[str, bool])
def delete_map(
    map_id: int,
    service: MapService = Depends(get_map_service),
) -> dict[str, bool]:
    # V2 delete treats missing IDs as a successful no-op.
    service.delete_map(map_id)
    return {"ok": True}


@router.post("/{map_id}/embed", response_model=EmbedResult)
def embed_map(
    map_id: int,
    service: MapService = Depends(get_map_service),
) -> EmbedResult:
    try:
        return service.embed_map(map_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
