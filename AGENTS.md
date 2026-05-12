# AGENTS.md

This repository's active application workspace is `v3/`.

## Current Direction

- Keep the current CarMaker-based research workflow.
- Do not plan or implement a CARLA transition unless explicitly requested.
- Preserve the V2 user experience while migrating implementation to:
  - SvelteKit/Svelte 5 frontend
  - Python/FastAPI backend
  - Electron as a thin desktop shell
- Treat `v2_legacy/` as archived reference code, not the primary implementation target.

## Main Paths

- `v3/apps/frontend/`: active SvelteKit frontend.
- `v3/apps/desktop-electron/`: Electron desktop shell.
- `v3/services/python-api/`: FastAPI backend.
- `docs/`: migration, parity, API mapping, and research notes.
- `CarMaker_RealtimeControl/`, `agent/`: CarMaker integration and automation references.
- `Paper_AGI_KSAE202601/`: paper source and research artifacts.

## Development Rules

- Start from the real files in `v3/` before changing behavior.
- Preserve existing UI/UX unless the task explicitly asks for redesign.
- Keep frontend/backend data contracts in camelCase for API payloads and TypeScript interfaces.
- Keep database/internal Python naming idiomatic for the layer being edited, but convert cleanly at API boundaries.
- Prefer existing stores, services, schemas, and route patterns over new abstractions.
- For frontend styling, inspect `v3/apps/frontend/src/app.css` before adding styles and reuse existing utility classes.
- Use Svelte 5 runes style where the surrounding component already uses it.
- Keep Electron responsible for shell/window/file-dialog concerns only.
- Keep application logic in the Python API or frontend stores, matching current ownership.
- For CarMaker work, preserve fail-closed behavior when command execution, telemetry, or trigger state is uncertain.

## Verification

- Frontend:
  - `cd v3/apps/frontend`
  - `npm run check`
  - `npm run build`
- Electron:
  - `cd v3/apps/desktop-electron`
  - `npm run lint`
- Python API:
  - `cd v3/services/python-api`
  - run the relevant pytest/API smoke checks if available.

## Generated Files

- Do not commit local agent metadata, caches, dependency folders, virtualenvs, or LaTeX build outputs.
- Paper source files such as `.tex`, `.bib`, figures, and manually maintained guide documents may be tracked when intentional.
