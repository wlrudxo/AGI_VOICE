# CarMaker Python Runtime Reference

## 기준 예제

- `runtime_minimal_example.py`
- `runtime_full_example.py`
- `simcontrol_connect_to_server_example.py`
- `simcontrol_full_example.py`
- `1_ReadWrite.py`
- `2_BasicCapturing.py`
- `3_CapturingWithDurationWatcher.py`
- `4_CapturingWithConditionWatcher.py`
- `5_CaptureToFile.py`
- `6_MultiFetch.py`

## 핵심 객체

- `Runtime`
- `Variation`
- `SimControlInteractive`
- `CarMaker`
- `simio`
- quantity condition / simstate condition

## 선택 규칙

- live control이 필요 없으면 `Runtime`
- 실행 중 quantity read/write, condition wait, live sensor coupling이 필요하면 `SimControlInteractive`
- capture/watcher는 runtime보다 simcontrol 문맥에서 설명하면 이해가 쉽다
