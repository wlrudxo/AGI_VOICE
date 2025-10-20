# AI Diet V2

> AI-powered desktop diet management application built with Tauri 2.x, SvelteKit, and Rust

AI Diet V2 is a comprehensive diet tracking application featuring natural language AI interactions, smart meal logging, exercise tracking, and personalized health insights—all in a beautiful desktop interface.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Tauri](https://img.shields.io/badge/Tauri-2.x-24C8DB)
![Svelte](https://img.shields.io/badge/Svelte-5.0-FF3E00)
![Rust](https://img.shields.io/badge/Rust-1.70+-orange)

## Features

### 🍽️ Smart Diet Tracking
- Record meals with detailed nutritional information (calories, protein, carbs, fat)
- Support for multiple meal types (breakfast, lunch, dinner, snacks, supplements)
- Daily and weekly nutrition summaries
- AI-powered meal logging via natural language

### 💪 Exercise & Weight Management
- Track workouts with duration and calorie estimates
- Daily weight monitoring
- Historical data visualization
- Progress tracking over time

### 🤖 AI Assistant
- **Natural Language Interface**: Chat with AI to log meals, check stats, and get insights
- **Dynamic Prompt System**: Customizable AI personality and behavior
- **Smart Command Templates**: Modular tag-based system for CRUD operations
- **Two-Pass Processing**: Intelligent READ → response flow for accurate data retrieval
- **Multi-Character Support**: Switch between different AI personalities

### 🎯 Mission System
- AI-generated health goals and challenges
- Progress tracking with status workflow (pending → in progress → completed)
- Personalized recommendations based on your data
- Daily/weekly/monthly AI evaluations

### 🪟 Desktop Experience
- **Widget Mode**: Compact chat-only interface (420x620px) for quick interactions
- **Custom Titlebar**: Native window controls with drag support
- **System Tray** (Ready): Minimize to tray, restore previous state
- **Auto-Refresh**: Real-time UI updates when AI modifies data
- **Dark Theme**: Beautiful purple gradient design

## Technology Stack

### Frontend
- **SvelteKit 2.9.0** - Full-stack web framework
- **Svelte 5.0** - Reactive UI with runes syntax
- **Tailwind CSS 4.1.14** - Utility-first styling
- **Vite 6.x** - Lightning-fast dev server
- **Iconify** - Solar duotone icon set
- **marked** - Markdown rendering for AI chat

### Backend
- **Tauri 2.x** - Rust-powered desktop framework
- **Rust 1.70+** - Systems programming language
- **SeaORM** - Async ORM for SQLite
- **SQLite** - Embedded database (`ai_diet.db`)

### AI Integration
- **Claude CLI** - Anthropic's Claude API via subprocess
- **Frontend-Driven Architecture** - Tag parsing and action execution in TypeScript
- **Dynamic Prompts** - Database-driven template system with variable substitution

## Quick Start

### Prerequisites

- **Node.js 18+** (for Vite and SvelteKit)
- **Rust 1.70+** (for Tauri backend)
- **Claude CLI** (for AI features)
  ```bash
  npm install -g @anthropic-ai/claude-cli
  ```
- **C++ Build Tools** (Windows only)

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd AI_Diet_V2

# 2. Install dependencies
npm install

# 3. Run development server
npm run tauri dev

# Or use the batch file (Windows)
start.bat
```

The application will:
1. Initialize the database (`ai_diet.db`) on first run
2. Create seed data (default character, prompt templates, commands)
3. Open the desktop application

### First-Time Setup

1. **Configure AI Chat** (optional):
   - Navigate to **AI Settings > Chat Settings**
   - Select your preferred character and system message
   - Add user information if desired

2. **Activate Command Templates**:
   - Go to **AI Settings > Commands**
   - Ensure at least one template is activated (green toggle)

3. **Start Logging**:
   - Use the AI chat: "점심에 치킨 먹었어" (Had chicken for lunch)
   - Or use the dedicated pages (Meals, Exercises, Weights)

## Development

### Project Structure

```
AI_Diet_V2/
├── src/                        # Frontend (SvelteKit + Svelte 5)
│   ├── routes/                 # Pages and layouts
│   ├── lib/
│   │   ├── components/         # Reusable UI components
│   │   ├── stores/             # State management
│   │   └── actions/            # AI tag parser & executor
│   └── app.css                 # Global styles + Tailwind
├── src-tauri/                  # Backend (Rust + Tauri)
│   ├── src/
│   │   ├── commands/           # Tauri commands (API layer)
│   │   ├── db/                 # Database models (SeaORM)
│   │   └── ai/                 # AI system (Claude CLI integration)
│   ├── Cargo.toml              # Rust dependencies
│   └── tauri.conf.json         # Tauri configuration
├── ai_diet.db                  # SQLite database (auto-created)
├── start.bat                   # Development launcher (Windows)
├── CLAUDE.md                   # Developer guide
└── ARCHITECTURE.md             # Detailed architecture documentation
```

### Running Development Server

```bash
# Start Tauri development mode (recommended)
npm run tauri dev

# Frontend only (for UI development)
npm run dev  # http://localhost:1420
```

### Building for Production

```bash
# Build desktop application
npm run tauri build

# Output location
# - Windows: src-tauri/target/release/bundle/nsis/ai_diet_v2_*.exe
# - macOS: src-tauri/target/release/bundle/macos/AI Diet V2.app
# - Linux: src-tauri/target/release/bundle/deb/ai-diet-v2_*.deb
```

### Testing

```bash
# Run Rust tests
cd src-tauri
cargo test

# Frontend tests (if configured)
npm test
```

## Usage

### AI Chat Examples

The AI assistant understands natural language commands:

```
You: "점심에 치킨 2000칼로리 먹었어"
AI: "치킨 맛있죠! 📋 식단 1개 추가됨 점심으로 기록했어요."

You: "어제 먹은 거 알려줘"
AI: "어제는 치킨과 샐러드를 드셨네요! 총 2300kcal 섭취하셨어요 😊"

You: "오늘 운동 30분 했어"
AI: "좋아요! 📋 운동 1개 추가됨 30분 런닝 완료! 💪 꾸준히 하시는 모습 멋져요!"
```

### Widget Mode

For quick interactions without opening the full app:

1. Click the **Widget** button in the titlebar
2. Window resizes to compact mode (420x620px)
3. Moves to bottom-right corner of screen
4. Only chat interface is visible
5. Click **Restore** to return to full app

### Database Management

The database file (`ai_diet.db`) is located in the project root.

**Inspect with SQLite**:
```bash
sqlite3 ai_diet.db
.tables
SELECT * FROM meals WHERE meal_date = '2025-10-18';
.exit
```

**Reset Database** (deletes all data):
```bash
# Delete the file and restart the app
rm ai_diet.db  # Unix/Mac
del ai_diet.db  # Windows
# Database will be recreated on next run
```

## Documentation

- **[CLAUDE.md](CLAUDE.md)** - Developer guide and coding conventions
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed system architecture (v2.0)
- **[Tauri Docs](https://tauri.app/)** - Tauri framework documentation
- **[Svelte 5 Docs](https://svelte-5-preview.vercel.app/)** - Svelte 5 runes syntax
- **[SeaORM Docs](https://www.sea-ql.org/SeaORM/)** - Rust ORM documentation

## Key Features Explained

### Frontend-Driven AI Architecture

Unlike traditional backends that handle AI response parsing, AI Diet V2 uses a **frontend-driven approach**:

1. **Rust Backend**: Assembles prompts, executes Claude CLI, returns raw response
2. **Frontend**: Parses tags, executes READ actions, sends results back to Claude
3. **Frontend**: Executes CUD (Create/Update/Delete) actions via Tauri commands

**Benefits**:
- Easier debugging (inspect tags in browser console)
- More flexible (add action types without backend changes)
- Better error handling and user feedback

### Dynamic Prompt System

AI behavior is fully customizable via database-stored templates:

- **System Messages**: Core AI instructions
- **Characters**: Personality and tone (e.g., "Aris from Blue Archive")
- **Command Templates**: Modular CRUD command sets (can be activated/deactivated)
- **User Info**: Personal context
- **Variable Substitution**: `{{user}}`, `{{char}}` in templates

### Auto-Refresh System

The UI automatically updates when the AI modifies data:

- Frontend polls DB timestamp every 2 seconds
- When database changes are detected, pages reload data
- No manual refresh needed
- Works even when app is in background

## Common Issues

### Claude CLI Not Found

```bash
# Install globally
npm install -g @anthropic-ai/claude-cli

# Verify
claude --version
```

### Command Templates Not Working

- Go to **AI Settings > Commands**
- Ensure at least one template is activated (green toggle)

### Build Errors (Rust)

```bash
# Update Rust
rustup update

# Clean and rebuild
cd src-tauri
cargo clean
cargo build
```

### Database Errors

Delete `ai_diet.db` and restart the app to recreate with fresh schema.

## Roadmap

### Phase 4: System Tray Integration
- [ ] Activate tray implementation
- [ ] Minimize to tray functionality
- [ ] Tray icon and menu

### Phase 5: Data Visualization
- [ ] Weight trend charts
- [ ] Calorie intake/burn graphs
- [ ] Weekly/monthly summaries
- [ ] Goal progress indicators

### Phase 6: Advanced AI Features
- [ ] Custom evaluation schedules
- [ ] Voice input/output
- [ ] Image recognition for food logging
- [ ] Multi-language support

### Phase 7: Cloud Sync
- [ ] Optional cloud backup
- [ ] Multi-device synchronization
- [ ] Data export/import

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Coding Standards**:
- Follow Rust conventions (rustfmt, clippy)
- Use Svelte 5 runes syntax (`$state`, `$derived`, `$effect`)
- Maintain snake_case for all data fields across frontend and backend
- Add tests for new features
- Update documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Tauri** - Amazing desktop framework
- **Anthropic** - Claude AI API
- **Svelte Team** - Reactive UI framework
- **SeaORM** - Excellent Rust ORM

## Support

For questions, issues, or feature requests:

- Open an [issue](https://github.com/yourusername/ai_diet_v2/issues)
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation
- Review [CLAUDE.md](CLAUDE.md) for development guidelines

---

**Made with ❤️ using Tauri, Svelte, and Rust**

**Version**: 2.0
**Last Updated**: 2025-10-18
**Status**: Full Tauri Migration Complete
