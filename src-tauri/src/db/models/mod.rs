// Re-export all entity modules
pub mod prompt_template;
pub mod character;
pub mod conversation;
pub mod message;
pub mod command_template;

// Prelude for easy imports
pub mod prelude {
    pub use super::prompt_template::Entity as PromptTemplate;
    pub use super::character::Entity as Character;
    pub use super::conversation::Entity as Conversation;
    pub use super::message::Entity as Message;
    pub use super::command_template::Entity as CommandTemplate;
}
