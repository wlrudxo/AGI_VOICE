use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, PartialEq, DeriveEntityModel, Serialize, Deserialize)]
#[sea_orm(table_name = "maps")]
#[serde(rename_all = "camelCase")]
pub struct Model {
    #[sea_orm(primary_key)]
    pub id: i32,

    #[sea_orm(unique)]
    pub name: String,

    pub description: String,
    pub node_xml: String,
    pub edge_xml: String,

    // Metadata
    #[sea_orm(column_type = "Text", nullable)]
    pub tags: Option<String>, // JSON array: ["intersection", "urban"]

    pub category: String, // intersection, highway, urban, rural
    pub difficulty: String, // easy, medium, hard

    #[sea_orm(column_type = "Text", nullable)]
    pub metadata: Option<String>, // JSON: {"author": "...", "notes": "..."}

    // Embedding status
    pub is_embedded: i32, // 0 or 1 (SQLite boolean)
    pub embedded_at: Option<DateTime>,
    #[sea_orm(column_type = "Text", nullable)]
    pub embedding_model: Option<String>,

    // Timestamps
    pub created_at: DateTime,
    pub updated_at: DateTime,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(has_many = "super::map_scenario::Entity")]
    Scenarios,
}

impl Related<super::map_scenario::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Scenarios.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}

// Default values
impl Default for Model {
    fn default() -> Self {
        Self {
            id: 0,
            name: String::new(),
            description: String::new(),
            node_xml: String::new(),
            edge_xml: String::new(),
            tags: None,
            category: "general".to_string(),
            difficulty: "medium".to_string(),
            metadata: None,
            is_embedded: 0,
            embedded_at: None,
            embedding_model: None,
            created_at: chrono::Utc::now().naive_utc(),
            updated_at: chrono::Utc::now().naive_utc(),
        }
    }
}
