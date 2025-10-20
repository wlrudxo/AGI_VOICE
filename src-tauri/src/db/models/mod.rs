// Re-export all entity modules
pub mod weight;
pub mod meal;
pub mod exercise;
pub mod ai_mission;
pub mod prompt_template;
pub mod character;
pub mod conversation;
pub mod message;
pub mod command_template;

// Prelude for easy imports
pub mod prelude {
    pub use super::weight::Entity as Weight;
    pub use super::meal::Entity as Meal;
    pub use super::exercise::Entity as Exercise;
    pub use super::ai_mission::Entity as AIMission;
    pub use super::prompt_template::Entity as PromptTemplate;
    pub use super::character::Entity as Character;
    pub use super::conversation::Entity as Conversation;
    pub use super::message::Entity as Message;
    pub use super::command_template::Entity as CommandTemplate;
}
