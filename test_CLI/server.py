"""
최소한의 Claude CLI 테스트 서버
"""
import sys
import io
import asyncio
import json
import logging
from pathlib import Path

# Windows 인코딩 문제 해결
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


async def call_claude(message: str) -> str:
    """Claude CLI 호출"""
    # CLAUDE.md 생성
    claude_md = """당신은 친절한 AI 어시스턴트입니다. 사용자의 질문에 간단하고 명확하게 답변하세요."""

    workspace = Path(__file__).parent
    claude_md_path = workspace / "CLAUDE.md"
    claude_md_path.write_text(claude_md, encoding='utf-8')

    logger.info(f"📝 CLAUDE.md 생성: {claude_md_path}")

    # Claude CLI 명령어
    cmd = 'claude -p --output-format stream-json --verbose --dangerously-skip-permissions --model sonnet --disallowedTools "TodoWrite,Task,Bash,WebSearch,WebFetch"'

    logger.info(f"🚀 Claude CLI 실행: {cmd}")

    # 프로세스 생성
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(workspace)
    )

    logger.info(f"✅ 프로세스 생성 (PID: {process.pid})")

    # 메시지 전송
    process.stdin.write(message.encode() + b'\n')
    await process.stdin.drain()
    process.stdin.close()
    await process.stdin.wait_closed()

    logger.info(f"📤 메시지 전송: {message}")

    # 응답 읽기
    full_response = ""
    buffer = b''

    while True:
        data = await process.stdout.read(1024)
        if not data:
            break

        buffer += data
        lines = buffer.split(b'\n')
        buffer = lines[-1]

        for line in lines[:-1]:
            decoded = line.decode('utf-8', errors='ignore').strip()
            if not decoded:
                continue

            try:
                json_data = json.loads(decoded)
                msg_type = json_data.get('type')

                # 델타 수집
                if msg_type == 'content_block_delta':
                    delta_text = json_data.get('delta', {}).get('text', '')
                    full_response += delta_text

                # 최종 응답
                elif msg_type == 'assistant':
                    content = json_data.get('message', {}).get('content', [])
                    if content and content[0].get('type') == 'text':
                        if not full_response:
                            full_response = content[0]['text']

            except json.JSONDecodeError:
                pass

    await process.wait()

    logger.info(f"📥 응답 수신: {full_response[:100]}...")

    return full_response


@app.get("/")
async def index():
    """간단한 HTML 페이지"""
    html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Claude CLI 테스트</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .chat-box {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
            min-height: 200px;
            max-height: 400px;
            overflow-y: auto;
            background: #fafafa;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
        }
        .user {
            background: #e3f2fd;
            text-align: right;
        }
        .assistant {
            background: #f1f8e9;
        }
        .input-group {
            display: flex;
            gap: 10px;
        }
        input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            padding: 10px 20px;
            background: #2196F3;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background: #1976D2;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .loading {
            text-align: center;
            color: #666;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Claude CLI 테스트</h1>
        <div class="chat-box" id="chatBox"></div>
        <div class="input-group">
            <input type="text" id="messageInput" placeholder="메시지를 입력하세요..." />
            <button id="sendBtn" onclick="sendMessage()">전송</button>
        </div>
    </div>

    <script>
        const chatBox = document.getElementById('chatBox');
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');

        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;

            // 사용자 메시지 표시
            addMessage('user', message);
            messageInput.value = '';
            sendBtn.disabled = true;

            // 로딩 표시
            const loadingId = Date.now();
            addMessage('loading', 'Claude가 생각중...', loadingId);

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });

                const data = await response.json();

                // 로딩 제거
                removeMessage(loadingId);

                // AI 응답 표시
                addMessage('assistant', data.response);

            } catch (error) {
                removeMessage(loadingId);
                addMessage('assistant', '❌ 오류: ' + error.message);
            } finally {
                sendBtn.disabled = false;
                messageInput.focus();
            }
        }

        function addMessage(type, text, id = null) {
            const div = document.createElement('div');
            div.className = `message ${type}`;
            div.textContent = text;
            if (id) div.id = `msg-${id}`;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function removeMessage(id) {
            const elem = document.getElementById(`msg-${id}`);
            if (elem) elem.remove();
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html)


@app.post("/chat")
async def chat(request: ChatRequest):
    """채팅 엔드포인트"""
    try:
        response = await call_claude(request.message)
        return {"response": response}
    except Exception as e:
        logger.error(f"❌ 오류: {e}", exc_info=True)
        return {"response": f"오류 발생: {str(e)}"}


if __name__ == "__main__":
    import uvicorn

    print("=" * 80)
    print("🚀 Claude CLI 테스트 서버 시작")
    print("=" * 80)
    print("📍 URL: http://localhost:9000")
    print("=" * 80)

    uvicorn.run(app, host="127.0.0.1", port=9000, reload=False)
