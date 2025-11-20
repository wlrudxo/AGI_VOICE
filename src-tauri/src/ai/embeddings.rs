use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::process::Command;

/// FAISS 인덱스 저장 경로 가져오기
pub fn get_faiss_index_path() -> Result<PathBuf, String> {
    let app_data = dirs::data_local_dir()
        .ok_or_else(|| "Cannot find AppData directory".to_string())?;

    let faiss_path = app_data.join("AGI_VOICE_V2").join("faiss_index");

    // Ensure directory exists
    if !faiss_path.exists() {
        std::fs::create_dir_all(&faiss_path)
            .map_err(|e| format!("Failed to create FAISS index directory: {}", e))?;
    }

    Ok(faiss_path)
}

/// 데이터베이스 경로 가져오기 (map_db.rs와 동일한 경로 사용)
pub fn get_db_path() -> Result<PathBuf, String> {
    // Use the same path as map_db.rs
    crate::db::map_db::get_map_db_path()
}

/// Python 스크립트 실행 헬퍼
async fn run_python_script(script_name: &str, args: Vec<String>) -> Result<String, String> {
    println!("🐍 Running Python script: {} with args: {:?}", script_name, args);

    // Try multiple possible paths for MapGenerator
    let exe_dir = std::env::current_exe()
        .map_err(|e| format!("Failed to get exe path: {}", e))?
        .parent()
        .ok_or_else(|| "Failed to get exe parent dir".to_string())?
        .to_path_buf();

    // Candidate paths (development and production)
    let mut candidates = vec![
        // Production: beside exe
        exe_dir.join("MapGenerator"),
    ];

    // Development: src-tauri/target/debug/../../../MapGenerator (project root)
    if let Some(project_root) = exe_dir
        .parent()  // target
        .and_then(|p| p.parent())  // src-tauri
        .and_then(|p| p.parent())  // AGI_VOICE_V2 (project root)
    {
        candidates.push(project_root.join("MapGenerator"));
    }

    // Current working directory
    if let Ok(cwd) = std::env::current_dir() {
        candidates.push(cwd.join("MapGenerator"));
    }

    let mut script_path = None;
    for candidate in &candidates {
        let full_path = candidate.join(script_name);
        println!("  Checking path: {:?}", full_path);
        if full_path.exists() {
            script_path = Some(full_path);
            break;
        }
    }

    let script_path = script_path.ok_or_else(|| {
        format!(
            "Python script not found: {}. Searched:\n{}",
            script_name,
            candidates
                .iter()
                .map(|p| format!("  - {:?}", p.join(script_name)))
                .collect::<Vec<_>>()
                .join("\n")
        )
    })?;

    println!("  Using script path: {:?}", script_path);

    let output = Command::new("python")
        .arg(script_path)
        .args(&args)
        .output()
        .map_err(|e| format!("Failed to execute Python: {}", e))?;

    // Log stderr (contains progress info)
    if !output.stderr.is_empty() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        println!("Python stderr:\n{}", stderr);
    }

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);

        // Check for OpenAI API key error
        if stderr.contains("api_key") || stderr.contains("OPENAI_API_KEY") {
            return Err("⚠️ API 키 설정이 필요합니다!\n\n프로젝트 루트의 .env 파일에 다음과 같이 설정하세요:\nOPENAI_API_KEY=sk-proj-xxxxxxxxxx\n\nAPI 키 발급: https://platform.openai.com/api-keys".to_string());
        }

        return Err(format!("Python script failed:\n{}", stderr));
    }

    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    println!("Python stdout: {}", stdout);

    Ok(stdout)
}

// ==================== Response Types ====================

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct EmbedResult {
    pub success: bool,
    pub map_id: Option<i32>,
    pub map_name: Option<String>,
    pub embedded_at: Option<String>,
    pub embedding_model: Option<String>,
    pub error: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct MapSearchResult {
    pub map_id: i32,
    pub map_name: String,
    pub description: String,
    pub category: String,
    pub difficulty: String,
    pub tags: Vec<String>,
    pub similarity_score: f32,
    pub distance: f32,
    pub is_embedded: bool,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BuildResult {
    pub success: bool,
    pub total_maps: Option<i32>,
    pub embedded_count: Option<i32>,
    pub skipped_count: Option<i32>,
    pub embedding_model: Option<String>,
    pub index_path: Option<String>,
    pub error: Option<String>,
}

// ==================== Tauri Commands ====================

/// 단일 맵 임베딩
#[tauri::command]
pub async fn embed_map(map_id: i32) -> Result<EmbedResult, String> {
    println!("📝 Embedding map: {}", map_id);

    let faiss_path = get_faiss_index_path()?
        .to_str()
        .ok_or_else(|| "Invalid FAISS path".to_string())?
        .to_string();

    let db_path = get_db_path()?
        .to_str()
        .ok_or_else(|| "Invalid DB path".to_string())?
        .to_string();

    let output = run_python_script(
        "embed_map.py",
        vec![map_id.to_string(), faiss_path, db_path],
    )
    .await?;

    let result: EmbedResult = serde_json::from_str(&output)
        .map_err(|e| format!("Failed to parse JSON response: {}", e))?;

    if result.success {
        println!("✅ Map embedded successfully: {}", map_id);
    } else {
        println!("❌ Failed to embed map: {:?}", result.error);
    }

    Ok(result)
}

/// 유사 맵 검색
#[tauri::command]
pub async fn search_similar_maps(
    query: String,
    top_k: Option<i32>,
) -> Result<Vec<MapSearchResult>, String> {
    println!("🔍 Searching for: '{}'", query);

    let faiss_path = get_faiss_index_path()?
        .to_str()
        .ok_or_else(|| "Invalid FAISS path".to_string())?
        .to_string();

    let db_path = get_db_path()?
        .to_str()
        .ok_or_else(|| "Invalid DB path".to_string())?
        .to_string();

    let k = top_k.unwrap_or(5).to_string();

    let output = run_python_script(
        "search_maps.py",
        vec![query.clone(), faiss_path, db_path, k],
    )
    .await?;

    let results: Vec<MapSearchResult> = serde_json::from_str(&output)
        .map_err(|e| format!("Failed to parse JSON response: {}", e))?;

    println!("✅ Found {} similar maps", results.len());

    Ok(results)
}

/// 전체 맵 일괄 임베딩
#[tauri::command]
pub async fn build_all_embeddings(rebuild: Option<bool>) -> Result<BuildResult, String> {
    println!("🏗️  Building all embeddings (rebuild: {:?})", rebuild);

    let faiss_path = get_faiss_index_path()?
        .to_str()
        .ok_or_else(|| "Invalid FAISS path".to_string())?
        .to_string();

    let db_path = get_db_path()?
        .to_str()
        .ok_or_else(|| "Invalid DB path".to_string())?
        .to_string();

    let mut args = vec![faiss_path, db_path];

    if rebuild.unwrap_or(false) {
        args.push("--rebuild".to_string());
    }

    let output = run_python_script("build_all_embeddings.py", args).await?;

    let result: BuildResult = serde_json::from_str(&output)
        .map_err(|e| format!("Failed to parse JSON response: {}", e))?;

    if result.success {
        println!("✅ All embeddings built successfully");
    } else {
        println!("❌ Failed to build embeddings: {:?}", result.error);
    }

    Ok(result)
}

/// Health check
#[tauri::command]
pub async fn embeddings_health() -> Result<String, String> {
    let faiss_path = get_faiss_index_path()?;
    let db_path = get_db_path()?;

    Ok(format!(
        "Embeddings module OK\nFAISS path: {:?}\nDB path: {:?}",
        faiss_path, db_path
    ))
}
