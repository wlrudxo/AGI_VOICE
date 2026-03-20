# AGI Voice V3 Desktop Shell

Minimal Electron shell for the V3 workspace.

## Assumptions

- Frontend dev server runs at `http://localhost:4173`
- Python backend runs at `http://127.0.0.1:8000`
- Backend health endpoint exists at `/health`
- If the frontend is not available yet, the shell loads a local fallback page instead.
- `npm run dev` works even before the frontend exists.

## Scripts

```bash
npm install
npm run dev
```

## Exposed bridge

- `window.desktop.window.*`
- `window.desktop.dialog.*`
- `window.desktop.fs.*`
- `window.desktop.shortcuts.*`
- `window.desktop.backend.ping()`
- `window.desktop.window.onEvent(handler)`
- `window.desktop.window.onCloseRequested(handler)`
- `window.desktop.window.close()`

## Notes

- This shell stays thin.
- App logic belongs in the Python backend.
- The renderer should talk to the backend through a small adapter layer, not directly to Electron APIs.
- The shell now works before the frontend exists, using `src/fallback.html`.
