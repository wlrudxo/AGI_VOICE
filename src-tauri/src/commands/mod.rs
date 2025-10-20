pub mod common;
pub mod utils;
pub mod ai_chat;
pub mod meals;
pub mod weights;
pub mod exercises;
pub mod missions;
pub mod dashboard;
pub mod settings;
pub mod prompt_templates;
pub mod characters;
pub mod conversations;
pub mod command_templates;

// Re-export common types
pub use common::*;

// Re-export Tauri commands
pub use ai_chat::*;
pub use meals::*;
pub use weights::*;
pub use exercises::*;
pub use missions::*;
pub use dashboard::*;
pub use settings::*;
pub use prompt_templates::*;
pub use characters::*;
pub use conversations::*;
pub use command_templates::*;
