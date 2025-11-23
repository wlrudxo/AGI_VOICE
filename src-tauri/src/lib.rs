use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    Manager,
};

// Database module
pub mod db;

// AI module
pub mod ai;

// Commands module
pub mod commands;

// CarMaker module
pub mod carmaker;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .invoke_handler(tauri::generate_handler![
            // AI Chat
            commands::chat,
            commands::chat_health,
            // Settings
            commands::get_settings,
            commands::update_settings,
            commands::settings_health,
            commands::get_chat_settings,
            commands::update_chat_settings,
            commands::get_db_timestamp,
            commands::sync_db_on_shutdown,
            // Database Management
            commands::export_db,
            commands::import_db,
            commands::get_db_info,
            commands::sync_db_now,
            commands::restore_backup,
            // Prompt Templates
            commands::get_prompt_templates,
            commands::get_prompt_template_by_id,
            commands::create_prompt_template,
            commands::update_prompt_template,
            commands::delete_prompt_template,
            commands::prompt_templates_health,
            // Characters
            commands::get_characters,
            commands::get_character_by_id,
            commands::create_character,
            commands::update_character,
            commands::delete_character,
            commands::characters_health,
            // Conversations
            commands::get_conversations,
            commands::get_conversation_by_id,
            commands::get_conversation_messages,
            commands::create_conversation,
            commands::update_conversation,
            commands::delete_conversation,
            commands::conversations_health,
            // Command Templates
            commands::get_command_templates,
            commands::get_command_template_by_id,
            commands::create_command_template,
            commands::update_command_template,
            commands::toggle_command_template,
            commands::delete_command_template,
            commands::command_templates_health,
            // Maps
            commands::create_map,
            commands::get_maps,
            commands::get_map_by_id,
            commands::update_map,
            commands::delete_map,
            commands::get_map_count,
            commands::maps_health,
            // Embeddings
            ai::embeddings::embed_map,
            ai::embeddings::search_similar_maps,
            ai::embeddings::build_all_embeddings,
            ai::embeddings::embeddings_health,
        ])
        .setup(|app| {
            // Initialize AI chat database connection
            let db = tauri::async_runtime::block_on(async {
                db::init_db().await
            });

            match db {
                Ok(connection) => {
                    println!("✅ AI Chat database initialized successfully");
                    app.manage(db::AiChatDb(connection));
                }
                Err(e) => {
                    eprintln!("❌ AI Chat database initialization failed: {}", e);
                    return Err(e.into());
                }
            }

            // Initialize map database connection
            let map_db = tauri::async_runtime::block_on(async {
                db::map_db::init_map_db().await
            });

            match map_db {
                Ok(connection) => {
                    println!("✅ Map database initialized successfully");
                    app.manage(db::MapDb(connection));
                }
                Err(e) => {
                    eprintln!("❌ Map database initialization failed: {}", e);
                    return Err(e.into());
                }
            }


            // 트레이 메뉴 생성
            let open_item = MenuItem::with_id(app, "open", "열기", true, None::<&str>)?;
            let widget_item = MenuItem::with_id(app, "widget", "위젯", true, None::<&str>)?;
            let quit_item = MenuItem::with_id(app, "quit", "종료", true, None::<&str>)?;

            let menu = Menu::with_items(
                app,
                &[&open_item, &widget_item, &quit_item],
            )?;

            // 트레이 아이콘 생성
            let _tray = TrayIconBuilder::new()
                .icon(app.default_window_icon().unwrap().clone())
                .menu(&menu)
                .show_menu_on_left_click(false)
                .on_menu_event(|app, event| {
                    use tauri::Emitter;
                    match event.id().as_ref() {
                        "open" => {
                            if let Some(window) = app.get_webview_window("main") {
                                let _ = window.show();
                                let _ = window.set_focus();
                                let _ = window.emit("tray-restore", ());
                            }
                        }
                        "widget" => {
                            if let Some(window) = app.get_webview_window("main") {
                                let _ = window.show();
                                let _ = window.set_focus();
                                let _ = window.emit("tray-widget", ());
                            }
                        }
                        "quit" => {
                            app.exit(0);
                        }
                        _ => {}
                    }
                })
                .on_tray_icon_event(|tray, event| {
                    use tauri::Emitter;
                    if let TrayIconEvent::Click {
                        button: MouseButton::Left,
                        button_state: MouseButtonState::Up,
                        ..
                    } = event
                    {
                        let app = tray.app_handle();
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                            let _ = window.emit("tray-restore", ());
                        }
                    }
                })
                .build(app)?;

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
