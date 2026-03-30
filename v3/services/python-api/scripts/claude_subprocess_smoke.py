import argparse
import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path

from app.services.chat import get_chat_service


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Direct Claude subprocess smoke test")
    parser.add_argument(
        "--model",
        default="sonnet",
        help="Claude model name",
    )
    parser.add_argument(
        "--prompt",
        default="안녕하세요. 1문장으로만 답해주세요.",
        help="Prompt to send directly to Claude CLI",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in seconds",
    )
    return parser.parse_args()


def run_blocking_stream(
    command: list[str],
    prompt: str,
    workspace_dir: Path,
    timeout_seconds: int,
) -> tuple[int, str, str]:
    process = subprocess.Popen(
        command,
        cwd=str(workspace_dir),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdin is not None
    process.stdin.write((prompt + "\n").encode("utf-8"))
    process.stdin.close()

    started_at = time.monotonic()
    stdout_chunks: list[str] = []
    stderr_chunks: list[str] = []
    full_response = ""

    assert process.stdout is not None
    while True:
        elapsed = time.monotonic() - started_at
        if elapsed >= timeout_seconds:
            process.terminate()
            try:
                _, stderr = process.communicate(timeout=2.0)
            except subprocess.TimeoutExpired:
                process.kill()
                _, stderr = process.communicate()
            stderr_text = stderr.decode("utf-8", errors="replace")
            if not stderr_text.strip():
                stderr_text = f"Timed out after {timeout_seconds}s"
            return 124, "".join(stdout_chunks), stderr_text

        line = process.stdout.readline()
        if not line:
            if process.poll() is not None:
                break
            time.sleep(0.05)
            continue

        decoded = line.decode("utf-8", errors="replace")
        stdout_chunks.append(decoded)
        stripped = decoded.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            continue

        msg_type = payload.get("type")
        if msg_type == "content_block_delta":
            delta = payload.get("delta", {})
            full_response += delta.get("text", "")
        elif msg_type == "assistant" and not full_response:
            content = payload.get("message", {}).get("content", [])
            if content:
                full_response = content[0].get("text", "")

    assert process.stderr is not None
    stderr_text = process.stderr.read().decode("utf-8", errors="replace")
    return process.returncode or 0, "".join(stdout_chunks), stderr_text


async def run_async(
    command: list[str],
    prompt: str,
    workspace_dir: Path,
    timeout_seconds: int,
) -> tuple[int, bytes, bytes]:
    process = await asyncio.create_subprocess_exec(
        *command,
        cwd=str(workspace_dir),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    assert process.stdin is not None
    process.stdin.write((prompt + "\n").encode("utf-8"))
    await process.stdin.drain()
    process.stdin.close()

    started_at = time.monotonic()
    while True:
        elapsed = time.monotonic() - started_at
        if elapsed >= timeout_seconds:
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=2.0)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
            stdout, stderr = await process.communicate()
            return 124, stdout, stderr or f"Timed out after {timeout_seconds}s".encode("utf-8")

        if process.returncode is not None:
            break

        await asyncio.sleep(0.1)

    stdout, stderr = await process.communicate()
    return process.returncode or 0, stdout, stderr


def main() -> int:
    args = parse_args()
    service = get_chat_service()
    workspace_dir = service._resolve_workspace_dir()  # type: ignore[attr-defined]
    claude_bin = service._resolve_claude_cli()  # type: ignore[attr-defined]
    if not claude_bin:
        print("RESULT=FAIL")
        print("ERROR=Claude CLI not found")
        return 1

    command = service._build_claude_command(  # type: ignore[attr-defined]
        claude_bin,
        [
            "-p",
            "--output-format",
            "stream-json",
            "--verbose",
            "--dangerously-skip-permissions",
            "--model",
            args.model,
            "--disallowedTools",
            "TodoWrite,Task,Bash,WebSearch,WebFetch",
        ],
    )

    print("== Claude Subprocess Smoke ==")
    print(f"python={sys.executable}")
    print(f"workspace_dir={workspace_dir}")
    print(f"claude_bin={claude_bin}")
    print(f"command={command}")
    print(f"timeout={args.timeout}")
    print(f"prompt={args.prompt}")

    if sys.platform.startswith("win"):
        returncode, stdout_text, stderr_text = run_blocking_stream(
            command, args.prompt, workspace_dir, args.timeout
        )
    else:
        returncode, stdout, stderr = asyncio.run(
            run_async(command, args.prompt, workspace_dir, args.timeout)
        )
        stdout_text = stdout.decode("utf-8", errors="replace")
        stderr_text = stderr.decode("utf-8", errors="replace")

    print(f"returncode={returncode}")
    print(f"stdout_len={len(stdout_text)}")
    print(f"stderr_len={len(stderr_text)}")
    print("--- STDOUT PREVIEW ---")
    print(stdout_text[:4000])
    print("--- STDERR PREVIEW ---")
    print(stderr_text[:4000])

    if returncode != 0:
        print("RESULT=FAIL")
        return 1

    print("RESULT=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
