use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, PartialEq, DeriveEntityModel, Serialize, Deserialize)]
#[sea_orm(table_name = "map_scenarios")]
#[serde(rename_all = "camelCase")]
pub struct Model {
    #[sea_orm(primary_key)]
    pub id: i32,

    pub map_id: i32,
    pub name: String,

    #[sea_orm(column_type = "Text", nullable)]
    pub description: Option<String>,

    // Scenario data (JSON)
    #[sea_orm(column_type = "Text", nullable)]
    pub drivers: Option<String>, // [{"id": "d1", "type": "aggressive"}]

    #[sea_orm(column_type = "Text", nullable)]
    pub vehicles: Option<String>, // [{"id": "v1", "model": "sedan"}]

    #[sea_orm(column_type = "Text", nullable)]
    pub traffic_config: Option<String>, // {"density": "high"}

    // Timestamps
    pub created_at: DateTime,
    pub updated_at: DateTime,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(
        belongs_to = "super::map::Entity",
        from = "Column::MapId",
        to = "super::map::Column::Id",
        on_delete = "Cascade"
    )]
    Map,
}

impl Related<super::map::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Map.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}
