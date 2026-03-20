# AGI Voice V3 Python API

Minimal FastAPI backend scaffold for the V3 rewrite.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## PowerShell

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Settings

- `APP_NAME`: app title shown by FastAPI
- `APP_VERSION`: service version string
- `API_HOST`: default `127.0.0.1`
- `API_PORT`: default `8000`
- `CORS_ORIGINS`: JSON list of frontend origins, default `["http://localhost:4173"]`

## Layout

- `app/main.py`: FastAPI entrypoint
- `app/core/config.py`: pydantic settings
- `app/api/routes/*`: placeholder routers for the V3 domains

## Endpoints

- `GET /health`
- `GET /api/chat/health`
- `GET /api/carmaker/health`
- `GET /api/triggers/health`
- `GET /api/settings/health`
- `GET /api/maps/health`
