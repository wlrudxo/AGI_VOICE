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
- `app/api/routes/*`: route modules for the V3 domains
- `app/services/carmaker.py`: first real CarMaker migration slice

## Endpoints

- `GET /health`
- `GET /api/chat/health`
- `GET /api/carmaker/health`
- `POST /api/carmaker/connect`
- `POST /api/carmaker/disconnect`
- `GET /api/carmaker/status`
- `GET /api/carmaker/monitoring`
- `POST /api/carmaker/monitoring`
- `GET /api/carmaker/telemetry`
- `POST /api/carmaker/command`
- `POST /api/carmaker/control/gas`
- `POST /api/carmaker/control/brake`
- `POST /api/carmaker/control/steer`
- `POST /api/carmaker/control/target-speed`
- `POST /api/carmaker/simulation/start`
- `POST /api/carmaker/simulation/stop`
- `GET /api/carmaker/watched-objects`
- `POST /api/carmaker/watched-objects`
- `DELETE /api/carmaker/watched-objects/{index}`
- `DELETE /api/carmaker/watched-objects`
- `GET /api/triggers/health`
- `GET /api/settings/health`
- `GET /api/maps/health`

## CarMaker Notes

- This is the first real V3 migration slice.
- The service keeps connection state in process memory.
- Telemetry currently uses on-demand reads and watched traffic objects only.
- Monitoring state is an in-memory compatibility flag for the current frontend contract.
- Thin wrapper control endpoints are implemented on top of raw command execution.
- WebSocket streaming and higher-level control endpoints will come later.
