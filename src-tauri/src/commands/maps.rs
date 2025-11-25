use sea_orm::*;
use serde::Deserialize;
use tauri::State;

use crate::db::models::map;
use crate::db::MapDb;

// ==================== Request/Response Models ====================

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CreateMapRequest {
    pub name: String,
    pub description: String,
    pub node_xml: String,
    pub edge_xml: String,
    pub tags: Option<Vec<String>>,
    pub category: Option<String>,
    pub difficulty: Option<String>,
    pub metadata: Option<serde_json::Value>,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct UpdateMapRequest {
    pub name: Option<String>,
    pub description: Option<String>,
    pub node_xml: Option<String>,
    pub edge_xml: Option<String>,
    pub tags: Option<Vec<String>>,
    pub category: Option<String>,
    pub difficulty: Option<String>,
    pub metadata: Option<serde_json::Value>,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct GetMapsQuery {
    pub category: Option<String>,
    pub is_embedded: Option<bool>,
    pub search: Option<String>,
}

// ==================== Tauri Commands ====================

/// Create a new map
#[tauri::command]
pub async fn create_map(
    request: CreateMapRequest,
    map_db: State<'_, MapDb>,
) -> Result<map::Model, String> {
    println!("📝 Creating map: {}", request.name);

    let now = chrono::Utc::now().naive_utc();

    // Convert tags to JSON string
    let tags_json = request.tags
        .map(|t| serde_json::to_string(&t).ok())
        .flatten();

    // Convert metadata to JSON string
    let metadata_json = request.metadata
        .map(|m| serde_json::to_string(&m).ok())
        .flatten();

    let new_map = map::ActiveModel {
        name: Set(request.name),
        description: Set(request.description),
        node_xml: Set(request.node_xml),
        edge_xml: Set(request.edge_xml),
        tags: Set(tags_json),
        category: Set(request.category.unwrap_or_else(|| "general".to_string())),
        difficulty: Set(request.difficulty.unwrap_or_else(|| "medium".to_string())),
        metadata: Set(metadata_json),
        is_embedded: Set(0),
        embedded_at: Set(None),
        embedding_model: Set(None),
        created_at: Set(now),
        updated_at: Set(now),
        ..Default::default()
    };

    let map = new_map.insert(&map_db.0).await.map_err(|e| {
        println!("❌ Failed to create map: {}", e);
        format!("Failed to create map: {}", e)
    })?;

    println!("✅ Map created: id={}, name={}", map.id, map.name);

    Ok(map)
}

/// Get all maps with optional filtering
#[tauri::command]
pub async fn get_maps(
    query: Option<GetMapsQuery>,
    map_db: State<'_, MapDb>,
) -> Result<Vec<map::Model>, String> {
    println!("📋 Getting maps");

    let mut select = map::Entity::find();

    // Apply filters
    if let Some(q) = query {
        if let Some(category) = q.category {
            select = select.filter(map::Column::Category.eq(category));
        }

        if let Some(is_embedded) = q.is_embedded {
            select = select.filter(map::Column::IsEmbedded.eq(if is_embedded { 1 } else { 0 }));
        }

        if let Some(search) = q.search {
            select = select.filter(
                Condition::any()
                    .add(map::Column::Name.contains(&search))
                    .add(map::Column::Description.contains(&search))
            );
        }
    }

    let maps = select
        .order_by_desc(map::Column::CreatedAt)
        .all(&map_db.0)
        .await
        .map_err(|e| {
            println!("❌ Failed to get maps: {}", e);
            format!("Failed to get maps: {}", e)
        })?;

    println!("✅ Found {} maps", maps.len());

    Ok(maps)
}

/// Get a single map by ID
#[tauri::command]
pub async fn get_map_by_id(
    id: i32,
    map_db: State<'_, MapDb>,
) -> Result<map::Model, String> {
    println!("🔍 Getting map by id: {}", id);

    let map = map::Entity::find_by_id(id)
        .one(&map_db.0)
        .await
        .map_err(|e| format!("Database error: {}", e))?
        .ok_or_else(|| format!("Map not found: {}", id))?;

    Ok(map)
}

/// Update a map
#[tauri::command]
pub async fn update_map(
    id: i32,
    request: UpdateMapRequest,
    map_db: State<'_, MapDb>,
) -> Result<map::Model, String> {
    println!("✏️ Updating map: {}", id);

    // Find existing map
    let existing = map::Entity::find_by_id(id)
        .one(&map_db.0)
        .await
        .map_err(|e| format!("Database error: {}", e))?
        .ok_or_else(|| format!("Map not found: {}", id))?;

    let mut active_model: map::ActiveModel = existing.into();

    // Update fields if provided
    if let Some(name) = request.name {
        active_model.name = Set(name);
    }
    if let Some(description) = request.description {
        active_model.description = Set(description);
    }
    if let Some(node_xml) = request.node_xml {
        active_model.node_xml = Set(node_xml);
    }
    if let Some(edge_xml) = request.edge_xml {
        active_model.edge_xml = Set(edge_xml);
    }
    if let Some(tags) = request.tags {
        active_model.tags = Set(serde_json::to_string(&tags).ok());
    }
    if let Some(category) = request.category {
        active_model.category = Set(category);
    }
    if let Some(difficulty) = request.difficulty {
        active_model.difficulty = Set(difficulty);
    }
    if let Some(metadata) = request.metadata {
        active_model.metadata = Set(serde_json::to_string(&metadata).ok());
    }

    active_model.updated_at = Set(chrono::Utc::now().naive_utc());

    // Clear embedding fields when map is updated (embedding needs to be regenerated)
    active_model.is_embedded = Set(0);
    active_model.embedded_at = Set(None);
    active_model.embedding_model = Set(None);

    let updated = active_model.update(&map_db.0).await.map_err(|e| {
        println!("❌ Failed to update map: {}", e);
        format!("Failed to update map: {}", e)
    })?;

    println!("✅ Map updated: id={}", updated.id);

    Ok(updated)
}

/// Delete a map
#[tauri::command]
pub async fn delete_map(
    id: i32,
    map_db: State<'_, MapDb>,
) -> Result<(), String> {
    println!("🗑️ Deleting map: {}", id);

    map::Entity::delete_by_id(id)
        .exec(&map_db.0)
        .await
        .map_err(|e| {
            println!("❌ Failed to delete map: {}", e);
            format!("Failed to delete map: {}", e)
        })?;

    println!("✅ Map deleted: id={}", id);

    Ok(())
}

/// Get map count
#[tauri::command]
pub async fn get_map_count(
    map_db: State<'_, MapDb>,
) -> Result<u64, String> {
    let count = map::Entity::find()
        .count(&map_db.0)
        .await
        .map_err(|e| format!("Failed to count maps: {}", e))?;

    Ok(count)
}

/// Health check
#[tauri::command]
pub async fn maps_health() -> Result<super::common::HealthResponse, String> {
    Ok(super::common::HealthResponse {
        status: "ok".to_string(),
        service: "maps".to_string(),
    })
}
