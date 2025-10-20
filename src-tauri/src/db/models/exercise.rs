use sea_orm::entity::prelude::*;

#[derive(Clone, Debug, PartialEq, DeriveEntityModel, serde::Serialize, serde::Deserialize)]
#[sea_orm(table_name = "exercises")]
pub struct Model {
    #[sea_orm(primary_key)]
    pub id: i32,
    pub exercise_date: Date,
    pub exercise_name: String,
    pub duration: i32,
    pub calories: Option<i32>,
    pub category: Option<String>,
    pub created_at: DateTime,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {}

impl ActiveModelBehavior for ActiveModel {}
