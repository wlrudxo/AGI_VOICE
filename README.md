# AGI Voice

현재 메인 앱 워크스페이스는 `v3/`입니다.

- 프런트엔드: SvelteKit
- 데스크톱 셸: Electron
- 백엔드: Python/FastAPI
- 목표: 기존 V2 UX를 유지하면서 Rust/Tauri 의존을 Python + Electron 구조로 전환

## 실행

Windows에서 개발 실행:

```bat
start.bat
```

또는 직접 실행:

```bat
v3\start_v3_dev.bat
```

각 서비스 개별 실행:

```bash
cd v3/apps/frontend
npm install
npm run dev
```

```bash
cd v3/services/python-api
python -m venv .venv
.venv\Scripts\activate
pip install -e .
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

```bash
cd v3/apps/desktop-electron
npm install
npm run dev
```

## CarMaker Map/Traffic Pipeline

CarMaker 도로 맵 생성, OpenDRIVE to RD5 변환, route/vehicle TestRun 생성을 묶은 실험용 앱은 아래 위치에 있습니다.

```bat
MapGenerator\CarMakerPipeline\carmaker_pipeline_app\run_app.bat
```

자세한 설명은 [`MapGenerator/CarMakerPipeline/README.md`](MapGenerator/CarMakerPipeline/README.md)와 [`docs/CARMAKER_MAP_TRAFFIC_PIPELINE.md`](docs/CARMAKER_MAP_TRAFFIC_PIPELINE.md)를 참고하세요.

## 구조

```text
AGI_VOICE/
├── v3/                     # 현재 메인 앱 워크스페이스
│   ├── apps/
│   │   ├── frontend/
│   │   └── desktop-electron/
│   ├── services/
│   │   └── python-api/
│   ├── packages/
│   └── scripts/
├── v2_legacy/              # 이전 루트 V2 앱 코드 보관 위치
├── docs/
├── MapGenerator/
│   └── CarMakerPipeline/   # CarMaker road/traffic generation pipeline
└── workspace/
    └── carmaker_llm_scenario_skill/
        ├── agent/          # CarMaker LLM research runner and direct-control tools
        └── references/     # IPG docs/skill source library and legacy notes
```

## 참고

- 이전 루트 앱 코드(`src`, `src-tauri`, `static`)는 `v2_legacy/`로 이동했습니다.
- Map/RAG는 V3에서 아직 별도 정리 중이며, 현재 메인 전환 범위에서는 완전 parity 대상으로 보지 않습니다.
