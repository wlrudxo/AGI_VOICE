# Claude CLI Rust Test (Subprocess Mode)

**Python 백엔드와 동일한 방식**으로 Rust에서 Claude CLI를 subprocess로 실행하는 테스트입니다.

## 🎯 테스트 목적

현재 Python 백엔드 (`backend/ai/claude_cli.py`)는 `claude` CLI를 subprocess로 실행합니다.
이 테스트는 **Rust로도 동일한 방식이 가능한지** 검증합니다.

## ⚙️ 사전 준비

### 1. Claude CLI 설치

```bash
# NPM으로 설치 (권장)
npm install -g @anthropic-ai/claude-code

# 설치 확인
claude --version
```

### 2. Claude CLI 인증

처음 사용 시 Claude CLI는 자동으로 인증을 요청합니다:

```bash
# 아무 프롬프트나 실행하여 인증
claude "hello"

# 브라우저가 열리면 Anthropic 계정으로 로그인
```

## 🚀 실행 방법

```bash
cd rust_test

# 빌드 및 실행
cargo run
```

## 📊 실행 흐름

### Python (현재 백엔드)
```python
# 1. subprocess 실행
process = await asyncio.create_subprocess_shell(
    'claude -p --output-format stream-json --model sonnet',
    stdin=PIPE, stdout=PIPE, stderr=PIPE
)

# 2. stdin으로 메시지 전송
process.stdin.write(message.encode() + b'\n')

# 3. stdout에서 JSON 스트림 읽기
while True:
    data = await process.stdout.read(1024)
    json_data = json.loads(line)
    if json_data['type'] == 'content_block_delta':
        full_text += json_data['delta']['text']
```

### Rust (이 테스트)
```rust
// 1. subprocess 실행
let mut child = Command::new("cmd")
    .args(&["/C", "claude -p --output-format stream-json ..."])
    .stdin(Stdio::piped())
    .stdout(Stdio::piped())
    .stderr(Stdio::piped())
    .spawn()?;

// 2. stdin으로 메시지 전송
let mut stdin = child.stdin.take()?;
stdin.write_all(message.as_bytes()).await?;

// 3. stdout에서 JSON 스트림 읽기
let mut reader = BufReader::new(stdout).lines();
while let Some(line) = reader.next_line().await? {
    let msg: StreamMessage = serde_json::from_str(&line)?;
    if msg.msg_type == "content_block_delta" {
        full_response.push_str(&msg.delta.text);
    }
}
```

## 🔧 코드 구조

### main.rs 주요 함수

**`call_claude_cli(message, model)`**
1. Claude CLI 프로세스 생성
2. stdin으로 메시지 전송
3. stdout에서 JSON 스트림 읽기
4. `content_block_delta` 타입의 델타 텍스트 수집
5. 전체 응답 반환

**환경변수** (Python과 동일):
- `FORCE_COLOR=0` - 색상 비활성화
- `NO_COLOR=1` - 색상 비활성화
- `CLAUDE_CODE_GIT_BASH_PATH` (Windows만) - Git Bash 경로

**명령어 옵션**:
```
claude -p
  --output-format stream-json
  --verbose
  --dangerously-skip-permissions
  --model sonnet
  --disallowedTools "TodoWrite,Task,Bash,WebSearch,WebFetch"
```

## 📝 예상 출력

```
🚀 Claude CLI Rust Test (Subprocess Mode)
============================================================

🔍 Checking if 'claude' CLI is installed...
✅ Claude CLI found: C:\Users\...\AppData\Roaming\npm\claude.cmd

============================================================
🎯 Test Configuration:
  Model: sonnet
  Message: Hello! Please respond with a simple greeting in Korean.
============================================================

🚀 Starting Claude CLI subprocess...
📝 Command: claude -p --output-format stream-json ...
✅ Process spawned (PID: Some(12345))

📤 Sending message to Claude...
Message: Hello! Please respond with a simple greeting in Korean.

📥 Reading response stream...
안녕하세요!

📊 Token usage: {"input_tokens":15,"output_tokens":8}

✅ Process exited with status: exit code: 0

============================================================
🤖 Claude's full response:
============================================================
안녕하세요!
============================================================

✅ Test completed successfully!
```

## ⚠️ 주의사항

1. **Claude CLI 설치 필수**
   - 없으면 프로그램이 자동으로 종료됩니다
   - `npm install -g @anthropic-ai/claude-code`

2. **인증 필요**
   - 첫 실행 시 브라우저에서 인증 필요
   - `claude "hello"` 명령으로 미리 인증 권장

3. **Git Bash (Windows)**
   - Claude CLI는 Windows에서 Git Bash를 사용합니다
   - 환경변수 `CLAUDE_CODE_GIT_BASH_PATH` 설정 필요

## 🎯 Python vs Rust 비교

| 항목 | Python | Rust |
|------|--------|------|
| subprocess 생성 | `asyncio.create_subprocess_shell` | `tokio::process::Command` |
| stdin 전송 | `process.stdin.write()` | `stdin.write_all().await` |
| stdout 읽기 | `process.stdout.read()` | `BufReader::new(stdout).lines()` |
| JSON 파싱 | `json.loads()` | `serde_json::from_str()` |
| 에러 핸들링 | try/except | Result<T, E> |
| 코드 라인 수 | ~220줄 | ~210줄 |

**결론**: Rust로도 Python과 **거의 동일한 방식**으로 구현 가능! ✅

## 🔄 다음 단계

이 테스트가 성공하면 전체 백엔드를 Rust로 이식할 수 있습니다:

1. ✅ **Claude CLI subprocess 호출** (이 테스트)
2. ⏳ SQLite 연동 (SeaORM)
3. ⏳ REST API (Axum)
4. ⏳ 태그 파싱 (regex)
5. ⏳ CRUD 액션 실행
6. ⏳ Tauri Command 통합

## 📚 참고

- Claude CLI 문서: https://docs.claude.com/claude-code
- Python 백엔드: `backend/ai/claude_cli.py`
- Tokio process: https://docs.rs/tokio/latest/tokio/process/
