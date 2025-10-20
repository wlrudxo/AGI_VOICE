# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AGI Voice V2 is a desktop research application for **AI-based autonomous driving map generation and driving decision research**. The application uses:
- **Frontend**: Tauri 2.x + SvelteKit 2.9.0 + Svelte 5.0.0 + Tailwind CSS 4.1.14 (with Vite 6.x)
- **Backend**: Tauri (Rust) + SeaORM with SQLite
- **Database**:
  - **AI Chat System**: SQLite (`ai_chat.db`) - Generic AI conversation system
  - **SUMO Maps**: SQLite (`sumo_maps.db`) - Autonomous driving map data
  - **Dual Database Support**: Wrapper types (`AiChatDb`, `MapDb`) for Tauri State management
- **Icons**: Iconify with Solar duotone theme
- **AI Integration**: Claude CLI via Tauri commands for natural language interactions

**Core Focus**:
- **Generic AI Chat System**: Reusable conversation system with dynamic prompts, characters, and command templates
- **Autonomous Driving Research**: Map generation and driving decision analysis using AI chat
- **Modular Architecture**: AI chat system separated from domain-specific data for reusability

## Architecture

### Naming Conventions

**CRITICAL**: This project uses **camelCase** for all data fields in Rust/Frontend communication (Tauri invoke).

#### Backend (Rust)
- All Rust structs use `#[serde(rename_all = "camelCase")]` for Tauri communication
- **Database columns remain snake_case**: `created_at`, `updated_at`, `is_active`, etc.
- SeaORM handles conversion between snake_case DB and camelCase Rust structs
- Tauri command parameters: `conversationId`, `messageId`, `templateId`
- Response fields: `messageCount`, `createdAt`, `updatedAt`, `isActive`

#### Frontend (TypeScript/Svelte)
- TypeScript interfaces must use camelCase: `conversationId`, `messageContent`, `createdAt`
- Form data objects must use camelCase: `{ conversationId, messageContent, createdAt }`
- Template access must use camelCase: `{conversation.messageCount}`, `{message.content}`
- Consistent with JavaScript/TypeScript conventions

#### Why camelCase?
- Standard JavaScript/TypeScript convention
- Tauri official examples use camelCase
- Frontend-first approach (most code is TypeScript/Svelte)
- Serde automatically converts: Rust snake_case fields → camelCase JSON → TypeScript camelCase
- **Database stays snake_case**: SeaORM models use Rust snake_case, serialization converts to camelCase

#### Migration Notes
- Old code may still have snake_case - convert to camelCase when encountered
- Common mistakes:
  - TypeScript interface uses camelCase but template uses snake_case → ERROR
  - FormData uses snake_case but Rust expects camelCase → Deserialization fails
  - Always verify both interface definition AND template usage match camelCase

### Frontend (Tauri + Svelte)
- **Framework**: SvelteKit 2.9.0 with Svelte 5.0.0 (using runes syntax: `$state`, `$derived`, `$effect`)
- **Styling**: Tailwind CSS 4.1.14 via `@tailwindcss/vite` plugin (v4 approach, not PostCSS)
- **Build Tool**: Vite 6.x with Tauri 2.x integration
- **Icons**: `@iconify/svelte` with Solar duotone icons
- **Main Pages**:
  - Dashboard (`/`) - Main interface with AI chat widget for autonomous driving research
  - Map Settings (`/map-settings/*`) - SUMO map management (generator, library)
  - AI Settings (`/ai-settings/*`) - AI system configuration (system messages, characters, commands, user info, final message)
  - Settings (`/settings`) - Application settings
- **State Management**:
  - Svelte stores (`src/lib/stores/`)
  - `uiStore.ts` - UI state (sidebar, chat, widget mode, conversation title)
  - `dbWatcher.svelte.ts` - DB change detection (2s polling, auto-refresh)
  - `settingsStore.ts` - App settings (minimize to tray)

### Backend (Tauri + Rust)
- **Framework**: Tauri 2.x with Rust
- **ORM**: SeaORM for SQLite database operations
- **Databases**:
  - **AI Chat DB**: `ai_chat.db` (Generic AI conversation system)
  - **Domain DB**: Separate databases for domain-specific data
- **Data Strategy**: Uses DateTime (UTC) for timestamp tracking
- **Communication**: Frontend communicates with Rust backend via Tauri `invoke()` commands
- **AI Integration**:
  - Claude CLI via subprocess (executed from Rust commands)
  - Dynamic prompt system: System Message + Character + Commands + User Info + Conversation History
  - 2-pass system: READ operations execute first, results fed back to Claude for natural language response
  - Tag-based CRUD system for structured actions (parsed and executed in frontend)

### Database Schema

**Database Architecture**:
- **AI Chat Database** (`ai_chat.db`): Generic, reusable AI conversation system
- **SUMO Maps Database** (`sumo_maps.db`): Autonomous driving map data
- **Dual Database Pattern**: Wrapper types to support multiple databases in Tauri State

**Important**: All timestamps use `DateTime` (UTC) for consistency.

**AI Chat System Tables** (`ai_chat.db` - Generic & Reusable):
- `prompt_templates` - System messages (templates for AI behavior)
- `characters` - Character prompts (personality/tone)
- `command_templates` - Command definitions (tag formats, action instructions)
- `conversations` - Chat sessions (links character + prompt template)
- `messages` - Chat history (user/assistant messages)

**SUMO Maps Tables** (`sumo_maps.db` - Domain-Specific):
- `maps` - SUMO traffic maps (name, description, node_xml, edge_xml, tags, category, difficulty, metadata, embedding info)
- `map_scenarios` - Map scenarios (map_id, drivers, vehicles, traffic_config)

**Dual Database Support**:
```rust
// Wrapper types for Tauri State management
pub struct AiChatDb(pub DatabaseConnection);
pub struct MapDb(pub DatabaseConnection);

// Commands use specific wrapper types
#[tauri::command]
pub async fn create_map(request: CreateMapRequest, map_db: State<'_, MapDb>) -> Result<map::Model, String>

#[tauri::command]
pub async fn get_conversations(db: State<'_, AiChatDb>) -> Result<Vec<ConversationWithCount>, String>
```

**Design Philosophy**:
- **Generic AI Chat**: All conversation-related tables in `ai_chat.db` for reusability across projects
- **Domain Separation**: Domain-specific data (e.g., autonomous driving maps, sensor data) in separate databases
- **No mixing**: AI chat system remains independent and portable
- **Type Safety**: Wrapper types prevent database connection mix-ups in Tauri State

### Dynamic Prompt System

The AI chat uses a **template-based dynamic prompt system** stored in the database:

1. **System Message** (prompt_templates): Core AI behavior and instructions
2. **Character** (characters): Personality, tone, and style (e.g., "Aris" from Blue Archive)
3. **Command Templates** (command_templates): Tag-based action instructions
   - Multiple templates can be created and activated/deactivated
   - Only active templates are sent to AI
   - Allows modular command sets for autonomous driving research tasks
4. **User Info**: User-specific context (stored in conversation or LocalStorage)
5. **Final Message**: Custom checkout instructions (stored in LocalStorage)
6. **Conversation History**: Previous messages for context continuity

**Prompt Assembly Flow**:
```
CLAUDE.md (saved to file):
  - System Message
  - Character Prompt
  - User Info

User Message (sent to Claude CLI):
  - Command Templates (active only)
  - Conversation History
  - Current Input
  - Final Message
```

## Development Commands

### Frontend (Tauri + Svelte)
```bash
npm install
npm run dev           # Vite dev server (http://localhost:1420)
npm run tauri dev     # Tauri desktop app
npm run tauri build   # Build desktop app
```

**Important Notes:**
- Tailwind CSS 4.x: Use `@import "tailwindcss";` (v4 syntax, not v3's `@tailwind` directives)
- Svelte 5: Use runes syntax (`$state`, `$derived`, `$effect` instead of `$:`)
- Icons: `@iconify/svelte` with Solar duotone theme

### Styling Guidelines

**IMPORTANT**: When developing components, **ALWAYS** use semantic utility classes defined in `src/app.css`.

#### Available Utility Classes

**Text Colors** (prefer these over inline styles):
```svelte
<!-- ✅ DO: Use utility classes -->
<h1 class="text-primary">Title</h1>
<p class="text-secondary">Description</p>
<span class="text-muted">Hint text</span>
<div class="text-accent">Highlighted text (primary color)</div>

<!-- ❌ DON'T: Use inline styles -->
<h1 style="color: var(--color-text-primary);">Title</h1>
```

**Background Colors**:
```svelte
<div class="bg-surface">White surface</div>
<div class="bg-surface-hover">Hover state</div>
<div class="bg-primary">Primary background</div>
<div class="bg-error">Error background</div>
<div class="bg-success">Success background</div>
```

**Border Colors**:
```svelte
<div class="border border-default">Default border</div>
<div class="border-2 border-primary">Primary border</div>
```

**Common Combinations**:
```svelte
<!-- Card component -->
<div class="card rounded-lg p-6 shadow-md">
  <h2 class="text-primary text-xl font-bold mb-4">Card Title</h2>
  <p class="text-secondary">Card content</p>
</div>
```

#### When to Use Inline Styles

Only use inline styles when:
1. The style doesn't have a utility class (e.g., `--color-background`, `--color-primary-bg-light`)
2. Dynamic styles based on JavaScript logic
3. Complex CSS that doesn't fit utility patterns

Example:
```svelte
<!-- ✅ Acceptable: No utility class exists -->
<div style="background-color: var(--color-background);">...</div>

<!-- ✅ Acceptable: Dynamic color -->
<div style="color: {mission.status === 'completed' ? 'var(--color-success)' : 'var(--color-error)'};">
  Status
</div>
```

#### Tailwind CSS v4 Restrictions

**DO NOT** use these (they don't work in Tailwind v4):
- `@layer utilities { ... }` - Use plain CSS classes instead
- `@apply bg-surface` inside `<style>` tags - Use `background-color: var(--color-surface);` directly
- Custom utilities in `@theme` - Define as regular CSS classes

#### Reference

All available CSS variables and utility classes are defined in `src/app.css`. Check this file first before writing new styles.

### Backend (Tauri + Rust)

**Backend Structure:**
```
src-tauri/
├── src/
│   ├── main.rs              # Tauri app entry point
│   ├── lib.rs               # Tauri command registration
│   ├── commands/
│   │   ├── mod.rs           # Command module exports
│   │   ├── ai_chat.rs       # AI chat command
│   │   ├── settings.rs      # Settings commands
│   │   ├── prompt_templates.rs   # System message CRUD
│   │   ├── characters.rs         # Character CRUD
│   │   ├── command_templates.rs  # Command template CRUD
│   │   ├── conversations.rs      # Conversation CRUD
│   │   └── maps.rs               # Map CRUD (SUMO maps)
│   ├── db/
│   │   ├── mod.rs           # Database initialization (AiChatDb, MapDb wrappers)
│   │   ├── map_db.rs        # SUMO maps database initialization
│   │   ├── models/          # SeaORM entity models
│   │   │   ├── mod.rs
│   │   │   ├── prompt_template.rs
│   │   │   ├── character.rs
│   │   │   ├── command_template.rs
│   │   │   ├── conversation.rs
│   │   │   ├── message.rs
│   │   │   ├── map.rs       # SUMO map entity
│   │   │   └── map_scenario.rs  # Map scenario entity
│   │   └── sync.rs          # Database sync utilities
│   └── ai/
│       ├── mod.rs           # AI module exports
│       ├── claude_cli.rs    # Claude CLI subprocess manager
│       └── prompt_builder.rs # Dynamic prompt assembly
├── Cargo.toml               # Rust dependencies
└── tauri.conf.json          # Tauri configuration
```


**Frontend Structure:**
```
src/
├── routes/
│   ├── +layout.svelte           # Main layout with sidebar
│   ├── +page.svelte             # Dashboard with AI chat
│   ├── ai-settings/
│   │   ├── +layout.svelte           # Sub-sidebar layout
│   │   ├── chat-settings/+page.svelte    # Chat settings
│   │   ├── system-messages/+page.svelte  # System message CRUD
│   │   ├── characters/+page.svelte       # Character CRUD
│   │   ├── commands/+page.svelte         # Command template CRUD
│   │   ├── user-info/+page.svelte        # User info management
│   │   └── final-message/+page.svelte    # Final message management
│   ├── map-settings/
│   │   ├── +layout.svelte           # Sub-sidebar layout (Map 설정)
│   │   ├── +page.svelte             # Default redirect to generator
│   │   ├── generator/+page.svelte   # SUMO map creation/editing
│   │   └── library/+page.svelte     # Map library with search/filter
│   └── settings/+page.svelte    # Settings
├── lib/
│   ├── components/
│   │   ├── TitleBar.svelte       # Custom titlebar with window controls & widget mode
│   │   ├── Sidebar.svelte        # Collapsible navigation (14rem ↔ 5.5rem)
│   │   ├── Tooltip.svelte        # Fixed-position tooltips
│   │   ├── AIChatWidget.svelte   # AI chat widget with history/chat views
│   │   ├── ChatView.svelte       # Chat interface with markdown rendering
│   │   ├── ChatHistoryView.svelte # Conversation history with message counts
│   │   ├── ChatSettingsView.svelte # Character/prompt selection modal
│   │   ├── MapCanvas.svelte      # SVG-based SUMO map visualization
│   │   └── MapCard.svelte        # Map display card (with edit/delete)
│   └── stores/
│       ├── uiStore.ts            # UI state (sidebar, chat, widget mode, conversation)
│       ├── dbWatcher.svelte.ts   # DB change detection (auto-refresh)
│       └── settingsStore.ts      # App settings (minimize to tray)
└── app.css                       # Global styles with Tailwind import
```


## Tauri Configuration

### Window Permissions (tauri.conf.json)

The app requires specific Tauri permissions for window management features:

```json
"permissions": [
  "core:window:allow-set-size",
  "core:window:allow-set-position",
  "core:window:allow-outer-size",
  "core:window:allow-outer-position",
  "core:window:allow-start-dragging",
  "core:window:allow-minimize",
  "core:window:allow-maximize",
  "core:window:allow-close",
  "core:window:allow-toggle-maximize",
  "core:window:allow-internal-toggle-maximize",
  "core:window:allow-current-monitor"
]
```

**Required for**:
- Custom titlebar with drag support
- Widget mode (resize/reposition window)
- Window controls (minimize, maximize, close)
- Double-click titlebar to maximize

## Windows Development Notes

### Claude CLI Subprocess Integration

The AI chat system uses Claude CLI via Rust's `std::process::Command`. On Windows, subprocess handling is automatically managed by Rust's standard library.

**Implementation**:
- Claude CLI is executed via `Command::new("claude")` in `src-tauri/src/ai/claude_cli.rs`
- UTF-8 encoding for emoji/Korean text is handled by Rust
- Temporary files are used for prompt assembly (CLAUDE.md)

## Key Features

### AI Chat System

**Dynamic Prompt Assembly** (Frontend-driven):
1. User sends message via Tauri `invoke('chat', { request })`
2. Rust backend loads from database:
   - System message (from prompt_templates table)
   - Character prompt (from characters table)
   - Active command templates (from command_templates table, `is_active=1`)
   - User info (from LocalStorage)
   - Conversation history (from messages table)
3. Assembles CLAUDE.md and user message
4. Executes Claude CLI subprocess with assembled prompts
5. Returns raw response to frontend
6. **Frontend parses response** for action tags
7. Frontend executes READ actions first (via Tauri invoke), feeds results back to Claude
8. Frontend executes CUD actions (Create/Update/Delete) via Tauri invoke
9. Messages are saved to database automatically

**Tag Format**: `<type|field:value|field:value|...>`
- Tags can be defined in command templates for specific autonomous driving research tasks
- Frontend parses and executes tagged actions via Tauri invoke commands

### Widget Mode

**Feature**: Compact chat-only interface with automatic window resizing

**Functionality**:
- Titlebar button activates widget mode
- Window resizes to 420x620px and moves to bottom-right corner
- All UI except chat widget is hidden
- Widget header shows:
  - Conversation title (or "새 채팅")
  - History/new chat/restore/close buttons
- Close button in widget mode exits the app (prepared for future tray support)
- Exit widget mode restores original window size and position

**Implementation**:
- `uiStore.isWidgetMode` tracks widget state
- `+layout.svelte` handles window resize via Tauri API
- `AIChatWidget.svelte` adapts UI based on widget mode
- Window size/position stored before entering widget mode

### Database Auto-Refresh

**Feature**: Frontend automatically refreshes when database changes (e.g., AI modifies data)

**Implementation**:
- Rust command: `get_db_timestamp` returns SQLite file modification time
- Frontend: `dbWatcher` store polls timestamp every 2 seconds via Tauri invoke
- Pages register onChange callbacks to reload data when DB changes
- **No manual refresh buttons needed** - all pages auto-refresh on DB changes

**Usage**:
```svelte
<script>
  import { onMount, onDestroy } from 'svelte';
  import { dbWatcher } from '$lib/stores/dbWatcher.svelte';

  let unsubscribe = null;

  onMount(() => {
    loadData();
    dbWatcher.startWatching();
    unsubscribe = dbWatcher.onChange(() => loadData());
  });

  onDestroy(() => {
    if (unsubscribe) unsubscribe();
  });
</script>
```

### Chat History with Message Counts

**Feature**: Conversation list displays message count for each chat

**Implementation**:
- Rust command: `get_conversations` includes `message_count` field
- Query counts messages for each conversation using SeaORM
- Frontend: Displays as "{time} • 메시지 {n}개"
- Real-time updates via `conversationCreated` event

### SUMO Map Management System

**Feature**: Create, visualize, and manage SUMO traffic simulation maps with full CRUD operations

**Architecture**:
- **Database**: Separate `sumo_maps.db` for domain-specific map data
- **Entity Models**: `map` (SUMO XML data) and `map_scenario` (vehicle/driver configs)
- **Dual Database Support**: Wrapper types (`AiChatDb`, `MapDb`) prevent State conflicts

**Backend (Rust)**:
- **Commands** (`src-tauri/src/commands/maps.rs`):
  - `create_map`: Save new SUMO map with XML data
  - `get_maps`: Retrieve maps with filtering (category, embedded status, search)
  - `get_map_by_id`: Get single map for editing
  - `update_map`: Update existing map
  - `delete_map`: Remove map from database
  - `get_map_count`: Get total map count

**Frontend (Svelte)**:
- **Map Settings Layout** (`/map-settings`):
  - Nested sidebar structure (like AI Settings)
  - Sub-menu: Map 생성, Map 라이브러리

- **Map Generator** (`/map-settings/generator`):
  - XML input panels for SUMO nodes and edges
  - Real-time map visualization with MapCanvas
  - Auto-parse XML on mount
  - Edit mode: Load existing map data via URL query param (`?id=123`)
  - Save/Update: Store to database with metadata

- **Map Library** (`/map-settings/library`):
  - Grid display of all saved maps using MapCard component
  - Search by name/description
  - Filter by category and embedding status
  - Real-time map count display
  - Auto-refresh on database changes (dbWatcher)
  - Edit button: Navigate to generator with map data pre-filled
  - Delete button: Remove map with confirmation

**Components**:
- **MapCanvas** (`src/lib/components/MapCanvas.svelte`):
  - SVG-based SUMO map visualization
  - Auto-scales to fit canvas
  - Displays nodes (circles) and edges (arrows with lanes)
  - Different colors for node types (traffic_light, priority)

- **MapCard** (`src/lib/components/MapCard.svelte`):
  - Card display for individual maps
  - Shows metadata: name, description, category, difficulty, tags
  - Embedding status badge (Phase 2)
  - Edit button (pen icon) - navigate to generator
  - Delete button (trash icon) - remove map

**Navigation Flow**:
```
[Main Sidebar]
├── Map 설정
    └── [Sub-sidebar]
        ├── Map 생성     → Create/Edit maps
        └── Map 라이브러리 → Browse/Manage maps
```

**SUMO XML Format**:
- **Nodes**: Junction/intersection definitions (id, x, y, type)
- **Edges**: Road connections (id, from, to, numLanes, speed)
- Parsed with DOMParser, visualized in SVG canvas

**Future Phases**:
- **Phase 2**: Embedding system with OpenAI API + FAISS vector DB
- **Phase 3**: RAG search functionality for map recommendations

## Common Issues & Solutions

### Issue: Command templates not working
**Cause**: All command templates are deactivated (`is_active=0`)
**Solution**: Activate at least one template in `/ai-settings/commands` page

### Issue: Database connection errors
**Cause**: Database file doesn't exist or is corrupted
**Solution**: Check that `ai_chat.db` exists in project root. Tauri creates it automatically on first run.

### Issue: Claude CLI not found
**Cause**: Claude CLI not installed or not in PATH
**Solution**: Install Claude CLI and ensure it's accessible via `claude` command in terminal

## Development Workflow

**Running the Application:**
```bash
# Development mode (with hot reload)
npm run tauri dev

# Production build
npm run tauri build
```

**Frontend only (for UI development):**
```bash
npm run dev  # Vite dev server on http://localhost:1420
```

**Testing AI Chat**:
- Use the built-in chat widget in the application
- Configure character and prompt template in `/ai-settings/chat-settings`
- Ensure Claude CLI is installed and accessible in PATH

---

**Last Updated**: 2025-10-20
**Project Status**: Autonomous Driving Research Application

**Recent Updates**:
- ✅ **SUMO Map Management System (Phase 1 Complete)**:
  - Dual database architecture (`ai_chat.db` + `sumo_maps.db`)
  - Wrapper types (`AiChatDb`, `MapDb`) for Tauri State management
  - Full CRUD operations for SUMO traffic maps
  - Map generator with XML input and SVG visualization
  - Map library with search, filter, and edit functionality
  - MapCanvas component (SVG-based visualization)
  - MapCard component (edit/delete buttons)
  - Nested sidebar structure (Map 설정 → Map 생성, Map 라이브러리)

- ✅ **Generic AI Chat System**:
  - Full dynamic prompt system with conversations, characters, and command templates
  - Database architecture: `ai_chat.db` for generic AI conversation system (reusable across projects)
  - Modular design: AI chat system separated from domain data for portability
  - Widget mode with window resizing and bottom-right positioning
  - Custom titlebar with window controls
  - Chat history with message counts
  - Auto-refresh system (2s polling via Tauri commands)

**Next Priority**:
- **Phase 2**: Implement embedding system for SUMO maps
  - OpenAI Embeddings API integration
  - FAISS vector database for similarity search
  - Embed button in map library
  - Embedding progress UI
- **Phase 3**: RAG search functionality for map recommendations
