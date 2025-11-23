use anyhow::{Context, Result};
use serde::Deserialize;
use std::env;
use std::path::PathBuf;
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

pub struct ClaudeCLIManager {
    workspace_dir: Option<PathBuf>,
    disallowed_tools: String,
}

impl ClaudeCLIManager {
    pub fn new(workspace_dir: Option<PathBuf>) -> Self {
        Self {
            workspace_dir,
            disallowed_tools: "TodoWrite,Task,Bash,WebSearch,WebFetch".to_string(),
        }
    }

    /// Resolve Git Bash path on Windows (user env -> PATH -> common installs)
    fn resolve_bash_path() -> Option<PathBuf> {
        // 1) User override
        if let Some(val) = env::var_os("CLAUDE_CODE_GIT_BASH_PATH") {
            let path = PathBuf::from(val);
            if path.exists() {
                return Some(path);
            }
        }

        // 2) PATH search
        if let Some(path) = env::var_os("PATH") {
            for dir in env::split_paths(&path) {
                let candidate = dir.join("bash.exe");
                if candidate.exists() {
                    return Some(candidate);
                }
            }
        }

        // 3) Common install locations
        let mut candidates = Vec::new();
        if let Some(pf) = env::var_os("ProgramFiles") {
            candidates.push(PathBuf::from(&pf).join("Git\\bin\\bash.exe"));
            candidates.push(PathBuf::from(&pf).join("Git\\usr\\bin\\bash.exe"));
        }
        if let Some(pfx86) = env::var_os("ProgramFiles(x86)") {
            candidates.push(PathBuf::from(&pfx86).join("Git\\bin\\bash.exe"));
            candidates.push(PathBuf::from(&pfx86).join("Git\\usr\\bin\\bash.exe"));
        }

        candidates.into_iter().find(|p| p.exists())
    }

    /// Claude CLI를 subprocess로 실행하여 응답 받기
    pub async fn chat(&self, message: &str, model: &str) -> Result<String> {
        println!("\n🚀 Starting Claude CLI subprocess...");

        // 명령어 구성 (Python과 동일)
        let cmd = format!(
            "claude -p --output-format stream-json --verbose --dangerously-skip-permissions --model {} --disallowedTools \"{}\"",
            model, self.disallowed_tools
        );

        println!("📝 Command: {}", cmd);

        // 환경변수 설정 + Windows/Unix 분기
        let mut child = if cfg!(target_os = "windows") {
            // Windows: cmd.exe로 실행
            let mut command = Command::new("cmd");
            command
                .args(&["/C", &cmd])
                .env("FORCE_COLOR", "0")
                .env("NO_COLOR", "1");

            if let Some(bash_path) = Self::resolve_bash_path() {
                println!("✅ Using Git Bash at: {}", bash_path.display());
                command.env("CLAUDE_CODE_GIT_BASH_PATH", bash_path);
            } else {
                println!("⚠️ Git Bash not found; relying on PATH");
            }

            if let Some(ref dir) = self.workspace_dir {
                command.current_dir(dir);
            }

            command
                .stdin(Stdio::piped())
                .stdout(Stdio::piped())
                .stderr(Stdio::piped())
                .spawn()
                .context("Failed to spawn Claude CLI process")?
        } else {
            // Unix: sh로 실행
            let mut command = Command::new("sh");
            command
                .args(&["-c", &cmd])
                .env("FORCE_COLOR", "0")
                .env("NO_COLOR", "1");

            if let Some(ref dir) = self.workspace_dir {
                command.current_dir(dir);
            }

            command
                .stdin(Stdio::piped())
                .stdout(Stdio::piped())
                .stderr(Stdio::piped())
                .spawn()
                .context("Failed to spawn Claude CLI process")?
        };

        println!("✅ Process spawned (PID: {:?})", child.id());

        // stdin으로 메시지 전송
        println!("\n📤 Sending message to Claude...");

        let mut stdin = child.stdin.take().context("Failed to open stdin")?;
        stdin.write_all(message.as_bytes()).await?;
        stdin.write_all(b"\n").await?;
        stdin.flush().await?;
        drop(stdin); // stdin 닫기

        // stdout 읽기 (JSON 스트림 - 라인별 파싱)
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

        // 응답 수집 (content_block_delta에서 델타 수집)
        let mut full_response = String::new();

        println!("\n📥 Reading response stream...");
        while let Some(line) = reader.next_line().await? {
            if line.trim().is_empty() {
                continue;
            }

            // JSON 파싱 시도
            if let Ok(msg) = serde_json::from_str::<StreamMessage>(&line) {
                match msg.msg_type.as_str() {
                    "content_block_delta" => {
                        // 델타 텍스트 수집
                        if let Ok(delta) = serde_json::from_value::<ContentBlockDelta>(msg.data) {
                            full_response.push_str(&delta.delta.text);
                        }
                    }
                    "assistant" => {
                        // 최종 응답 (검증용 - 델타 수집 실패 시 사용)
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
                        // 토큰 사용량 로깅
                        if let Some(usage) = msg.data.get("usage") {
                            println!("📊 Token usage: {}", usage);
                        }
                    }
                    _ => {
                        // 다른 타입 무시
                    }
                }
            }
        }

        // stderr 태스크 완료 대기
        let _ = stderr_task.await;

        // 프로세스 종료 대기
        let status = child.wait().await?;
        println!("✅ Process exited with status: {}", status);

        Ok(full_response)
    }
}
