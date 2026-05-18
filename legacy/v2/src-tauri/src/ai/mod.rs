pub mod claude_cli;
pub mod prompt_builder;
pub mod embeddings;

pub use claude_cli::ClaudeCLIManager;
pub use prompt_builder::{build_full_prompt, save_claude_md, Message};
