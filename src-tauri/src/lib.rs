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

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .invoke_handler(tauri::generate_handler![
            // AI Chat
            commands::chat,
            commands::chat_health,
            // Meals
            commands::get_meals,
            commands::get_meal_by_id,
            commands::get_meals_by_date,
            commands::get_meal_stats,
            commands::create_meal,
            commands::update_meal,
            commands::delete_meal,
            commands::delete_meals_by_date,
            // Weights
            commands::get_weights,
            commands::get_weight_by_id,
            commands::get_weight_by_date,
            commands::create_weight,
            commands::update_weight,
            commands::update_weight_by_date,
            commands::delete_weight,
            commands::delete_weight_by_date,
            // Exercises
            commands::get_exercises,
            commands::get_exercise_by_id,
            commands::get_exercises_by_date,
            commands::get_exercise_stats,
            commands::create_exercise,
            commands::update_exercise,
            commands::delete_exercise,
            commands::delete_exercises_by_date,
            // Missions
            commands::get_missions,
            commands::get_mission_by_id,
            commands::get_mission_stats,
            commands::create_mission,
            commands::update_mission,
            commands::update_mission_status,
            commands::delete_mission,
            // Dashboard
            commands::get_dashboard,
            commands::get_weekly_dashboard,
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
        ])
        .setup(|app| {
            // Initialize database connection
            let db = tauri::async_runtime::block_on(async {
                db::init_db().await
            });

            match db {
                Ok(connection) => {
                    println!("✅ Database initialized successfully");
                    app.manage(connection);
                }
                Err(e) => {
                    eprintln!("❌ Database initialization failed: {}", e);
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
