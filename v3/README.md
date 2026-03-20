# AGI Voice V3 Workspace

This directory is the isolated workspace for AGI Voice V3.

V3 goals:

- keep the V2 frontend user experience unchanged
- replace the Rust/Tauri backend with a Python-centered backend
- use Electron only as a thin desktop shell
- allow V2 and V3 to coexist during migration

## Layout

```text
v3/
├── apps/
│   ├── desktop-electron/   # Electron shell
│   └── frontend/           # Future frontend migration target
├── packages/
│   └── shared-contracts/   # Shared API contracts and types
├── scripts/                # Workspace helper scripts
└── services/
    └── python-api/         # FastAPI backend
```

## Current Status

- `apps/desktop-electron`: scaffolded
- `services/python-api`: scaffolded
- `apps/frontend`: placeholder only
- `packages/shared-contracts`: placeholder only

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

- The Electron shell targets `http://localhost:4173` when a frontend is available.
- If the frontend is not up yet, Electron falls back to a local placeholder page.
- The Python API default is `http://127.0.0.1:8000`.
- A V3 frontend scaffold has not been created yet.

## Migration Principle

V3 is not a redesign. It is a backend migration.

- preserve user-facing UI/UX
- replace Tauri command dependencies with Python API and Electron preload bridges
- move app logic into Python incrementally
