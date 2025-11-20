use chrono::{Datelike, Local, Timelike, Weekday};
use std::fs;
use std::path::{Path, PathBuf};

/// 메시지 구조체 (DB models와 독립적으로 정의)
#[derive(Debug, Clone)]
pub struct Message {
    pub role: String,
    pub content: String,
    pub timestamp: Option<String>,
}

/// 변수 치환 ({{user}}, {{char}})
fn substitute_variables(text: &str, user_name: &str, char_name: &str) -> String {
    text.replace("{{user}}", user_name)
        .replace("{{char}}", char_name)
}

/// 이전 대화 메시지 포맷팅 (system 메시지 제외, 타임스탬프 포함)
fn format_previous_messages(messages: &[Message]) -> String {
    // system 메시지는 Previous Exchanges에서 제외
    let user_assistant_only: Vec<&Message> = messages
        .iter()
        .filter(|msg| msg.role != "system")
        .collect();

    if user_assistant_only.is_empty() {
        return "[Start a new chat]".to_string();
    }

    let mut formatted = Vec::new();

    for msg in user_assistant_only {
        let role = &msg.role;
        let content = &msg.content;
        let timestamp = msg.timestamp.as_deref().unwrap_or("");

        if role == "user" {
            formatted.push(format!(
                r#"      {{
      "role": "user",
      "timestamp": "{}",
      "parts": [
        {{
          "text": "{}"
        }}
      ]
    }}"#,
                timestamp, content
            ));
        } else if role == "assistant" {
            formatted.push(format!(
                r#"    {{
      "role": "model",
      "timestamp": "{}",
      "parts": [
        {{
          "text": "{}"
        }}
      ]
    }}"#,
                timestamp, content
            ));
        }
    }

    formatted.join(",\n")
}

/// 동적으로 전체 프롬프트 조립
///
/// # Arguments
/// * `system_message` - 시스템 메시지 (프롬프트 템플릿)
/// * `character_prompt` - 캐릭터 프롬프트
/// * `user_info` - 유저 정보
/// * `command_info` - 명령어 정보 리스트 (활성화된 템플릿들)
/// * `previous_messages` - 이전 대화 리스트
/// * `current_input` - 현재 사용자 입력
/// * `final_message` - 최종 체크리스트 메시지
/// * `system_context` - 시스템 컨텍스트 (READ 결과 등)
/// * `user_name` - 유저 이름 (변수 치환용)
/// * `char_name` - 캐릭터 이름 (변수 치환용)
///
/// # Returns
/// (claude_md_content, full_user_message) 튜플
/// * `claude_md_content` - CLAUDE.md로 저장할 내용
/// * `full_user_message` - Claude CLI에 전달할 전체 메시지
pub fn build_full_prompt(
    system_message: &str,
    character_prompt: &str,
    user_info: &str,
    command_info: &[String],
    previous_messages: &[Message],
    current_input: &str,
    final_message: Option<&str>,
    system_context: Option<&str>,
    user_name: &str,
    char_name: &str,
) -> (String, String) {
    // CLAUDE.md 내용 조립 (System Message + Character + User Information)
    let mut claude_md = String::new();

    claude_md.push_str("## System Message\n\n");
    claude_md.push_str(system_message.trim());
    claude_md.push_str("\n\n");

    claude_md.push_str("## Character\n\n");
    claude_md.push_str(character_prompt.trim());
    claude_md.push_str("\n\n");

    if !user_info.trim().is_empty() {
        claude_md.push_str("## User Information\n\n");
        claude_md.push_str(user_info.trim());
        claude_md.push_str("\n\n");
    }

    // 전체 유저 메시지 조립 (명령어 정보 + 이전 대화 + 현재 입력)
    let mut full_message = String::new();

    // 명령어 정보 (여러 개를 합쳐서 출력)
    if !command_info.is_empty() {
        full_message.push_str("## 명령어 정보\n\n");
        for cmd in command_info {
            full_message.push_str(cmd.trim());
            full_message.push_str("\n\n");
        }
    }

    // 이전 대화
    full_message.push_str("<--Previous Exchanges Start-->\n\n");
    let formatted_history = format_previous_messages(previous_messages);
    full_message.push_str(&formatted_history);
    full_message.push_str("\n\n<--Previous Response End-->\n\n");
    full_message.push_str("Do not include the content of this response, but continue the story after this response.\n\n");

    // 현재 입력 (system 컨텍스트가 있으면 system만, 없으면 current_input 사용)
    full_message.push_str("## Current Input\n\n```\n\n");

    if let Some(ctx) = system_context {
        if !ctx.trim().is_empty() {
            // system_context가 있으면 (READ 결과) 원래 입력은 이미 previous에 있으므로 제외
            full_message.push_str("## System Message\n\n");
            full_message.push_str(ctx.trim());
        } else {
            full_message.push_str(current_input.trim());
        }
    } else {
        // 첫 번째 호출이면 current_input 사용
        full_message.push_str(current_input.trim());
    }

    full_message.push_str("\n\n```\n<--## Current Input End-->\n\n");

    // Final Checkout (사용자 정의 또는 기본값)
    if let Some(msg) = final_message {
        if !msg.trim().is_empty() {
            full_message.push_str(msg.trim());
            full_message.push_str("\n\n");
        } else {
            // 기본 Final Checkout
            full_message.push_str("## Final Checkout\n\n");
            full_message.push_str("- Check if all required tags are properly formatted\n");
            full_message.push_str("- Ensure the response is friendly and encouraging\n");
            full_message.push_str("- Verify date formats (YYYY-MM-DD)\n\n");
        }
    } else {
        // 기본 Final Checkout
        full_message.push_str("## Final Checkout\n\n");
        full_message.push_str("- Check if all required tags are properly formatted\n");
        full_message.push_str("- Ensure the response is friendly and encouraging\n");
        full_message.push_str("- Verify date formats (YYYY-MM-DD)\n\n");
    }

    // Current Time 추가
    let now = Local::now();
    let weekday = match now.weekday() {
        Weekday::Mon => "월요일",
        Weekday::Tue => "화요일",
        Weekday::Wed => "수요일",
        Weekday::Thu => "목요일",
        Weekday::Fri => "금요일",
        Weekday::Sat => "토요일",
        Weekday::Sun => "일요일",
    };

    full_message.push_str(&format!(
        "## Current Time\n{}년 {}월 {}일 {} {}시 {}분\n",
        now.year(),
        now.month(),
        now.day(),
        weekday,
        now.hour(),
        now.minute()
    ));

    // 변수 치환 (마지막 단계)
    let claude_md = substitute_variables(&claude_md, user_name, char_name);
    let full_message = substitute_variables(&full_message, user_name, char_name);

    (claude_md, full_message)
}

/// CLAUDE.md를 저장
///
/// # Arguments
/// * `content` - CLAUDE.md 내용
/// * `workspace_dir` - 저장할 디렉토리 (None이면 AppData/agi_voice_v2 사용)
///
/// # Returns
/// 저장된 파일 경로
pub fn save_claude_md(content: &str, workspace_dir: Option<&Path>) -> Result<PathBuf, std::io::Error> {
    let target_dir = if let Some(dir) = workspace_dir {
        dir.to_path_buf()
    } else {
        // Default to AppData directory if no workspace specified
        crate::db::get_app_data_dir()
            .map_err(|e| std::io::Error::new(std::io::ErrorKind::NotFound, e))?
    };

    let claude_md_path = target_dir.join("CLAUDE.md");

    fs::write(&claude_md_path, content)?;

    Ok(claude_md_path)
}
