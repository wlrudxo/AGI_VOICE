use anyhow::{Context, Result};
use serde::Deserialize;
use std::process::Stdio;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use tokio::process::Command;

// Claude CLI JSON 스트림 응답 타입들
#[derive(Debug, Deserialize)]
struct StreamMessage {
    #[serde(rename = "type")]
    msg_type: String,
    #[serde(flatten)]
    data: serde_json::Value,
}

#[derive(Debug, Deserialize)]
struct ContentBlockDelta {
    delta: Delta,
}

#[derive(Debug, Deserialize)]
struct Delta {
    text: String,
}

/// Claude CLI를 subprocess로 실행하여 응답 받기
async fn call_claude_cli(message: &str, model: &str) -> Result<String> {
    println!("\n🚀 Starting Claude CLI subprocess...");

    // 명령어 구성 (Python과 동일)
    let disallowed_tools = "TodoWrite,Task,Bash,WebSearch,WebFetch";
    let cmd = format!(
        "claude -p --output-format stream-json --verbose --dangerously-skip-permissions --model {} --disallowedTools \"{}\"",
        model, disallowed_tools
    );

    println!("📝 Command: {}", cmd);

    // 환경변수 설정
    let mut child = if cfg!(target_os = "windows") {
        // Windows: cmd.exe로 실행
        Command::new("cmd")
            .args(&["/C", &cmd])
            .env("FORCE_COLOR", "0")
            .env("NO_COLOR", "1")
            .env("CLAUDE_CODE_GIT_BASH_PATH", "C:\\Program Files\\Git\\bin\\bash.exe")
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .context("Failed to spawn Claude CLI process")?
    } else {
        // Unix: sh로 실행
        Command::new("sh")
            .args(&["-c", &cmd])
            .env("FORCE_COLOR", "0")
            .env("NO_COLOR", "1")
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .context("Failed to spawn Claude CLI process")?
    };

    println!("✅ Process spawned (PID: {:?})", child.id());

    // stdin으로 메시지 전송
    println!("\n📤 Sending message to Claude...");
    println!("Message: {}", message);

    let mut stdin = child.stdin.take().context("Failed to open stdin")?;
    stdin.write_all(message.as_bytes()).await?;
    stdin.write_all(b"\n").await?;
    stdin.flush().await?;
    drop(stdin); // stdin 닫기

    // stdout 읽기 (JSON 스트림)
    let stdout = child.stdout.take().context("Failed to open stdout")?;
    let mut reader = BufReader::new(stdout).lines();

    // stderr 읽기 (백그라운드)
    let stderr = child.stderr.take().context("Failed to open stderr")?;
    let stderr_task = tokio::spawn(async move {
        let mut stderr_reader = BufReader::new(stderr).lines();
        while let Ok(Some(line)) = stderr_reader.next_line().await {
            if !line.trim().is_empty() {
                eprintln!("[Claude stderr] {}", line);
            }
        }
    });

    // 응답 수집
    let mut full_response = String::new();

    println!("\n📥 Reading response stream...");
    while let Some(line) = reader.next_line().await? {
        if line.trim().is_empty() {
            continue;
        }

        // JSON 파싱 시도
        match serde_json::from_str::<StreamMessage>(&line) {
            Ok(msg) => {
                match msg.msg_type.as_str() {
                    "content_block_delta" => {
                        // 델타 텍스트 수집
                        if let Ok(delta) = serde_json::from_value::<ContentBlockDelta>(msg.data) {
                            full_response.push_str(&delta.delta.text);
                            print!("{}", delta.delta.text); // 실시간 출력
                        }
                    }
                    "assistant" => {
                        // 최종 응답 (검증용)
                        if let Some(content) = msg.data.get("message")
                            .and_then(|m| m.get("content"))
                            .and_then(|c| c.as_array())
                        {
                            if let Some(first) = content.first() {
                                if let Some(text) = first.get("text").and_then(|t| t.as_str()) {
                                    if full_response.is_empty() {
                                        full_response = text.to_string();
                                    }
                                }
                            }
                        }
                    }
                    "result" => {
                        // 토큰 사용량 출력
                        if let Some(usage) = msg.data.get("usage") {
                            println!("\n\n📊 Token usage: {}", usage);
                        }
                    }
                    _ => {
                        // 다른 타입 무시
                    }
                }
            }
            Err(_) => {
                // JSON이 아닌 줄은 무시 (또는 로그 출력)
                // println!("[Non-JSON] {}", line);
            }
        }
    }

    // stderr 태스크 완료 대기
    let _ = stderr_task.await;

    // 프로세스 종료 대기
    let status = child.wait().await?;
    println!("\n\n✅ Process exited with status: {}", status);

    Ok(full_response)
}

#[tokio::main]
async fn main() -> Result<()> {
    println!("🚀 Claude CLI Rust Test (Subprocess Mode)");
    println!("{}", "=".repeat(60));

    // Claude CLI 설치 확인
    println!("\n🔍 Checking if 'claude' CLI is installed...");
    let check = if cfg!(target_os = "windows") {
        Command::new("cmd").args(&["/C", "where claude"]).output().await
    } else {
        Command::new("which").arg("claude").output().await
    };

    match check {
        Ok(output) if output.status.success() => {
            let path = String::from_utf8_lossy(&output.stdout);
            println!("✅ Claude CLI found: {}", path.trim());
        }
        _ => {
            eprintln!("❌ Claude CLI not found!");
            eprintln!("Please install Claude CLI first:");
            eprintln!("  npm install -g @anthropic-ai/claude-code");
            return Ok(());
        }
    }

    // 테스트 메시지
    let test_message = "Hello! Please respond with a simple greeting in Korean.";
    let model = "sonnet";

    println!("\n{}", "=".repeat(60));
    println!("🎯 Test Configuration:");
    println!("  Model: {}", model);
    println!("  Message: {}", test_message);
    println!("{}", "=".repeat(60));

    // Claude CLI 호출
    match call_claude_cli(test_message, model).await {
        Ok(response) => {
            println!("\n{}", "=".repeat(60));
            println!("🤖 Claude's full response:");
            println!("{}", "=".repeat(60));
            println!("{}", response);
            println!("{}", "=".repeat(60));
            println!("\n✅ Test completed successfully!");
        }
        Err(e) => {
            eprintln!("\n❌ Error: {:?}", e);
            return Err(e);
        }
    }

    Ok(())
}
