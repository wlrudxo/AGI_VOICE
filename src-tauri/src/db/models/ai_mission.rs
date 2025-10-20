use sea_orm::entity::prelude::*;

#[derive(Clone, Debug, PartialEq, DeriveEntityModel, serde::Serialize, serde::Deserialize)]
#[sea_orm(table_name = "ai_missions")]
pub struct Model {
    #[sea_orm(primary_key)]
    pub id: i32,
    pub mission_title: String,
    pub description: Option<String>,
    pub status: String,
    pub ai_comment: Option<String>,
    pub completion_comment: Option<String>,
    pub deadline: Option<Date>,
    pub created_at: DateTime,
    pub start_date: Option<DateTime>,
    pub completed_at: Option<DateTime>,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {}

impl ActiveModelBehavior for ActiveModel {}
