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
- **CarMaker Integration**: Real-time vehicle control and monitoring with trigger-based automation
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
  - Map Settings (`/map-settings/*`) - SUMO map management (generator, library, rag-test)
  - AI Settings (`/ai-settings/*`) - AI system configuration (system messages, characters, commands, user info, final message)
  - Autonomous Driving (`/autonomous-driving/*`) - CarMaker integration (vehicle-control, manual-control, triggers, settings)
  - App Settings (`/app-settings`) - Application settings (DB, backup, Claude workspace)
- **State Management**:
  - Svelte stores (`src/lib/stores/`)
  - `uiStore.ts` - UI state (sidebar, chat, widget mode, conversation title)
  - `dbWatcher.svelte.ts` - DB change detection (2s polling, auto-refresh)
  - `settingsStore.ts` - App settings (minimize to tray)
  - `dialogStore.svelte.ts` - Dialog management (confirm/alert)
  - `aiConfigStore.ts` - AI configuration (character/prompt selection)
  - `carmakerStore.svelte.ts` - CarMaker connection and vehicle state
  - `triggerMonitor.svelte.ts` - Trigger monitoring and evaluation

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
2. **Character** (characters): Personality, tone, and style
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

**CRITICAL**: Before creating or modifying ANY component:

1. **READ `src/app.css` COMPLETELY** to understand all available utility classes
2. **USE existing utility classes** instead of creating new styles
3. **ADD to app.css** only if the style is reusable across multiple components
4. **AVOID duplicate styles** - search app.css first before writing CSS

**IMPORTANT**: When developing components, **ALWAYS** use semantic utility classes defined in `src/app.css`.

#### Must-Read Before Development

**Before writing ANY styles, read the ENTIRE `src/app.css` file to see:**
- All color variables (--color-*)
- All utility classes (.btn-*, .text-*, .bg-*, .section-*, .table-*, etc.)
- Component patterns (toggle-switch, alert boxes, sliders, etc.)
- Layout helpers (page-header, sub-sidebar, etc.)

**This prevents duplicate code and ensures consistency.**

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

#### Complete Utility Class Reference (src/app.css)

**MUST READ `src/app.css` before development!** The file contains:

**Buttons**: `.btn-primary`, `.btn-secondary`, `.btn-danger`, `.btn-icon`, `.btn-text`
**Text Colors**: `.text-primary`, `.text-secondary`, `.text-muted`, `.text-accent`, `.text-accent-dark`
**Backgrounds**: `.bg-surface`, `.bg-surface-hover`, `.bg-primary`, `.bg-error`, `.bg-success`, `.bg-warning`, `.bg-info`, `.bg-info-box`
**Borders**: `.border-default`, `.border-dark`, `.border-primary`
**Cards**: `.card`, `.card-hover`
**Forms**: `.input-field`, `.select-field`, `.toggle-switch`, `.toggle-switch-track`, `.toggle-switch-thumb`
**Alerts**: `.alert-success`, `.alert-error`, `.alert-info`, `.alert-warning`
**Layouts**: `.page-header`, `.page-description`, `.section`, `.section-header`, `.section-title`
**Sub-Sidebar**: `.sub-sidebar-layout`, `.sub-sidebar`, `.sub-sidebar-header`, `.sub-nav`, `.sub-nav-item`, `.sub-sidebar-footer`, `.sub-sidebar-toggle-btn`
**Status**: `.status-indicator`, `.status-dot` (with `.connected`, `.warning` modifiers)
**Controls**: `.slider` (range input with custom thumb)
**Tables**: `.table`, `.table-wrapper` (with sticky header support)
**Logs**: `.log-container`, `.log-message`
**Scrollbar**: Custom webkit scrollbar styles

**Development Workflow**:
1. Open `src/app.css` and read through ALL utility classes
2. Use existing classes in your component
3. Only add component-specific styles in `<style>` tags
4. If a pattern is used 2+ times, add it to app.css

**Example - Good Practice**:
```svelte
<script>
  // Before writing styles, developer read app.css and found:
  // - .page-header exists
  // - .section exists
  // - .btn-primary exists
  // - .table exists
</script>

<div class="page-header">
  <h1>My Page</h1>
  <p class="page-description">Description here</p>
</div>

<section class="card section">
  <h2 class="section-title text-primary">Data</h2>
  <div class="table-wrapper">
    <table class="table">...</table>
  </div>
</section>

<style>
  /* Only component-specific styles here */
  .my-unique-layout {
    display: grid;
    grid-template-columns: 2fr 1fr;
  }
</style>
```

**Example - Bad Practice**:
```svelte
<!-- ❌ DON'T: Recreating existing utility classes -->
<style>
  .my-header {
    margin-bottom: 2rem;  /* This is .page-header! */
  }

  .my-section {
    border-radius: 0.75rem;  /* This is .section! */
    padding: 1.5rem;
    box-shadow: var(--shadow-sm);
  }

  .my-button {
    background: var(--color-primary);  /* This is .btn-primary! */
    color: white;
    padding: 0.5rem 1rem;
  }
</style>
```

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
│   │   ├── conversations.rs # Conversation CRUD
│   │   ├── characters.rs    # Character CRUD
│   │   ├── prompt_templates.rs   # System message CRUD
│   │   ├── command_templates.rs  # Command template CRUD
│   │   ├── maps.rs          # Map CRUD (SUMO maps)
│   │   ├── carmaker_control.rs   # CarMaker vehicle control
│   │   ├── triggers.rs      # Trigger management
│   │   ├── settings.rs      # Settings commands
│   │   ├── common.rs        # Shared command utilities
│   │   └── utils.rs         # Helper functions (DB timestamp, etc.)
│   ├── db/
│   │   ├── mod.rs           # Database initialization (AiChatDb, MapDb wrappers)
│   │   ├── map_db.rs        # SUMO maps database initialization
│   │   ├── schema.rs        # Database schema definitions
│   │   ├── seed_data.rs     # Default data seeding
│   │   ├── sync.rs          # Database sync utilities
│   │   └── models/          # SeaORM entity models
│   │       ├── mod.rs
│   │       ├── conversation.rs
│   │       ├── message.rs
│   │       ├── prompt_template.rs
│   │       ├── character.rs
│   │       ├── command_template.rs
│   │       ├── map.rs       # SUMO map entity
│   │       └── map_scenario.rs  # Map scenario entity
│   ├── ai/
│   │   ├── mod.rs           # AI module exports
│   │   ├── claude_cli.rs    # Claude CLI subprocess manager
│   │   ├── prompt_builder.rs # Dynamic prompt assembly
│   │   └── embeddings.rs    # OpenAI embeddings integration
│   ├── carmaker/
│   │   ├── mod.rs           # CarMaker module exports
│   │   ├── client.rs        # CarMaker TCP client
│   │   └── types.rs         # CarMaker data types
│   └── triggers/
│       ├── mod.rs           # Trigger module exports
│       ├── state.rs         # Trigger state management
│       └── types.rs         # Trigger data types
├── Cargo.toml               # Rust dependencies
└── tauri.conf.json          # Tauri configuration
```


**Frontend Structure:**
```
src/
├── routes/
│   ├── +layout.svelte           # Main layout with sidebar
│   ├── +layout.ts               # Layout load function
│   ├── +page.svelte             # Dashboard with AI chat
│   ├── ai-settings/
│   │   ├── +layout.svelte           # Sub-sidebar layout
│   │   ├── +page.svelte             # Redirect to chat-settings
│   │   ├── +page.server.ts          # Server-side redirect
│   │   ├── chat-settings/+page.svelte    # Chat settings
│   │   ├── system-messages/+page.svelte  # System message CRUD
│   │   ├── characters/+page.svelte       # Character CRUD
│   │   ├── commands/+page.svelte         # Command template CRUD
│   │   ├── user-info/+page.svelte        # User info management
│   │   └── final-message/+page.svelte    # Final message management
│   ├── map-settings/
│   │   ├── +layout.svelte           # Sub-sidebar layout
│   │   ├── +page.svelte             # Redirect to generator
│   │   ├── generator/+page.svelte   # SUMO map creation/editing
│   │   ├── library/+page.svelte     # Map library with search/filter
│   │   └── rag-test/+page.svelte    # RAG system testing
│   ├── autonomous-driving/
│   │   ├── +layout.svelte           # Sub-sidebar layout
│   │   ├── +page.svelte             # Redirect to vehicle-control
│   │   ├── +page.server.ts          # Server-side redirect
│   │   ├── vehicle-control/+page.svelte  # Real-time vehicle control
│   │   ├── manual-control/+page.svelte   # Manual vehicle control
│   │   ├── triggers/+page.svelte         # Trigger management
│   │   └── settings/+page.svelte         # CarMaker settings
│   └── app-settings/+page.svelte  # Application settings
├── lib/
│   ├── components/
│   │   ├── TitleBar.svelte       # Custom titlebar with window controls
│   │   ├── Sidebar.svelte        # Collapsible navigation (14rem ↔ 5.5rem)
│   │   ├── Tooltip.svelte        # Fixed-position tooltips
│   │   ├── Dialog.svelte         # Generic dialog component
│   │   ├── HelpModal.svelte      # Help/documentation modal
│   │   ├── AIChatWidget.svelte   # AI chat widget (3 views)
│   │   ├── ChatView.svelte       # Chat interface with markdown
│   │   ├── ChatHistoryView.svelte # Conversation history
│   │   ├── ChatSettingsView.svelte # Character/prompt selection
│   │   ├── MapCanvas.svelte      # SVG SUMO map visualization
│   │   └── MapCard.svelte        # Map display card
│   ├── stores/
│   │   ├── uiStore.ts            # UI state (sidebar, chat, widget)
│   │   ├── dbWatcher.svelte.ts   # DB change detection
│   │   ├── settingsStore.ts      # App settings
│   │   ├── dialogStore.svelte.ts # Dialog state management
│   │   ├── aiConfigStore.ts      # AI configuration state
│   │   ├── carmakerStore.svelte.ts # CarMaker connection & state
│   │   └── triggerMonitor.svelte.ts # Trigger monitoring
│   ├── actions/
│   │   ├── parser.ts             # Tag parser (AI response → actions)
│   │   ├── executor.ts           # Action executor (invoke Tauri)
│   │   ├── formatter.ts          # Result formatter
│   │   ├── vehicleCommandParser.ts # Vehicle command parser
│   │   └── vehicleCommandExecutor.ts # Vehicle command executor
│   ├── utils/
│   │   └── triggerEvaluator.ts   # Trigger condition evaluator
│   └── config.ts                 # App configuration
└── app.css                       # Global styles + Tailwind import
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
        ├── Map 라이브러리 → Browse/Manage maps
        └── RAG 테스트   → Test RAG system (Phase 3)
```

**SUMO XML Format**:
- **Nodes**: Junction/intersection definitions (id, x, y, type)
- **Edges**: Road connections (id, from, to, numLanes, speed)
- Parsed with DOMParser, visualized in SVG canvas

**Future Phases**:
- **Phase 2**: Embedding system with OpenAI API + FAISS vector DB
- **Phase 3**: RAG search functionality for map recommendations

### CarMaker LLM Control System

**Feature**: AI-based vehicle control with trigger-based automation

**Architecture**:
- **Parser**: `src/lib/actions/vehicleCommandParser.ts` - Parse LLM responses into executable commands
- **Executor**: `src/lib/actions/vehicleCommandExecutor.ts` - Execute commands via CarMaker TCP connection
- **Trigger Monitor**: `src/lib/stores/triggerMonitor.svelte.ts` - Monitor vehicle state and activate triggers
- **CarMaker Store**: `src/lib/stores/carmakerStore.svelte.ts` - Manage TCP connection and vehicle data

**Unified Command Format** (inspired by `CarMaker_RealtimeControl/llm_integration.py`):

```
DM.Gas = <value> | <duration_ms> [| <mode>]
DM.Brake = <value> | <duration_ms> [| <mode>]
DM.Steer.Ang = <value> | <duration_ms> [| <mode>]
wait <milliseconds>
wait_until <condition>
```

**Format Rules**:
- **Required**: `variable = value | duration`
- **Optional**: `| mode` (defaults to `Abs`)
- **Duration**: MUST be specified in milliseconds
- **Modes**: `Abs`, `Off`, `Fac`, `AbsRamp`, `FacRamp`
- **Sequential Execution**: All commands execute top-to-bottom
- **Wait**: Use `wait <ms>` for explicit delays between commands
- **Wait Until**: Use `wait_until <condition>` to wait for vehicle state (not implemented yet)

**Examples**:

1. **Simple Deceleration**:
```
DM.Gas = 0.0 | 500 | Abs
DM.Brake = 0.3 | 2000 | Abs
```

2. **Sequence with Delays**:
```
DM.Gas = 0.8 | 1000 | Abs
wait 500
DM.Brake = 0.2 | 2000
wait 1000
DM.Gas = 0.0 | 500
```

3. **Different Control Modes**:
```
DM.Gas = 0.5 | 1000 | Fac
DM.Brake = 0.3 | 2000 | AbsRamp
DM.Steer.Ang = 0.1 | 1500 | Off
```

**Legacy Format Support**:
- Old format `DM.Gas = 0.5` (without duration) is supported with default 2000ms and Abs mode
- Console warning shown for legacy format usage

**Trigger System**:
1. **Monitor**: 10Hz polling of vehicle telemetry data
2. **Evaluate**: Check trigger conditions against current vehicle state
3. **Pause**: Simulation pauses (time scale = 0.001x) when trigger activates
4. **LLM/Rule**: Request AI response OR execute predefined rule commands
5. **Resume**: Simulation resumes (time scale = 1.0x) + execute commands
6. **Cooldown**: 5-second reset period to prevent duplicate trigger activation

**LLM Prompt Template** (triggerMonitor.svelte.ts:232-265):
- System sends vehicle data snapshot to AI
- AI responds with command sequence in unified format
- Commands are parsed and executed sequentially
- Logs shown in trigger monitor and chat view

**Testing**:
- Test suite: `src/lib/actions/vehicleCommandParser.test.ts`
- Run: `npx tsx src/lib/actions/vehicleCommandParser.test.ts`
- All test cases validate unified format parsing

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

**Last Updated**: 2025-11-22
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
  - Nested sidebar structure (Map 설정 → Map 생성, Map 라이브러리, RAG 테스트)
  - RAG test page placeholder for Phase 3

- ✅ **Generic AI Chat System**:
  - Full dynamic prompt system with conversations, characters, and command templates
  - Database architecture: `ai_chat.db` for generic AI conversation system (reusable across projects)
  - Modular design: AI chat system separated from domain data for portability
  - Widget mode with window resizing and bottom-right positioning
  - Custom titlebar with window controls
  - Chat history with message counts
  - Auto-refresh system (2s polling via Tauri commands)
  - Action processing system (parser, executor, formatter)
  - Dialog component for confirmations and alerts

- ✅ **Code Architecture**:
  - Created ARCHITECTURE.md with detailed technical documentation
  - Complete project structure documentation (frontend/backend)
  - Data flow diagrams and state management patterns
  - Naming conventions and migration guidelines

**Next Priority**:
- **Phase 2**: Implement embedding system for SUMO maps
  - OpenAI Embeddings API integration
  - FAISS vector database for similarity search
  - Embed button in map library
  - Embedding progress UI
- **Phase 3**: RAG search functionality for map recommendations
  - Semantic search implementation
  - Context-aware map recommendations
