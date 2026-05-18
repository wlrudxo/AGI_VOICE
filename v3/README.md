# AGI Voice V3 Workspace

This is the active AGI Voice application workspace.

Goals:

- keep the V2 frontend user experience unchanged
- replace the Rust/Tauri backend with a Python-centered backend
- use Electron only as a thin desktop shell
- retain legacy V2 code separately under `../legacy/v2`

## Layout

```text
v3/
├── apps/
│   ├── desktop-electron/   # Electron shell
│   └── frontend/           # Active frontend
├── packages/
│   └── shared-contracts/   # Shared API contracts and types
├── scripts/                # Workspace helper scripts
└── services/
    └── python-api/         # FastAPI backend
```

## Current Status

- `apps/frontend`: active main UI
- `apps/desktop-electron`: active desktop shell
- `services/python-api`: active backend
- `packages/shared-contracts`: reserved for shared contracts

## Dev Startup

Run each part independently for now.

### Windows One-Click Startup

From Windows Explorer or a terminal, run:

```bat
v3\start_v3_dev.bat
```

This opens three separate consoles for:

- frontend
- Python API
- Electron shell

The batch file does not install dependencies automatically.
If something is missing, each console prints the required setup step.

### Python API

```bash
cd v3/services/python-api
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Electron Shell

```bash
cd v3/apps/desktop-electron
npm install
npm run dev
```

Notes:

- The Electron shell targets `http://127.0.0.1:4173` when a frontend is available.
- If the frontend is not up yet, Electron falls back to a local placeholder page.
- The Python API default is `http://127.0.0.1:8000`.
## Migration Principle

V3 is not a redesign. It is the main app workspace after the backend migration.

- preserve user-facing UI/UX
- replace Tauri command dependencies with Python API and Electron preload bridges
- move app logic into Python incrementally
