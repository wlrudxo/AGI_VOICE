use serde::Serialize;

/// Common response for delete operations
#[derive(Debug, Serialize)]
pub struct DeleteResult {
    pub message: String,
}

/// Common health check response
#[derive(Debug, Serialize)]
pub struct HealthResponse {
    pub status: String,
    pub service: String,
}
