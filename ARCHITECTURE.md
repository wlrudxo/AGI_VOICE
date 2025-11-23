# ARCHITECTURE.md

This document describes the technical architecture of AGI Voice V2.

## Technology Stack

### Frontend
- **Framework**: Tauri 2.x + SvelteKit 2.9.0 + Svelte 5.0.0 (runes syntax)
- **Build Tool**: Vite 6.x
- **Styling**: Tailwind CSS 4.1.14 (via `@tailwindcss/vite` plugin)
- **Icons**: `@iconify/svelte` with Solar duotone theme
- **Communication**: Tauri IPC (`invoke()` commands)

### Backend
- **Runtime**: Tauri (Rust)
- **ORM**: SeaORM with SQLite
- **Databases**:
  - `ai_chat.db` - Generic AI conversation system
  - `sumo_maps.db` - Autonomous driving map data
- **AI Integration**: Claude CLI via subprocess
- **State Management**: Tauri State with wrapper types (`AiChatDb`, `MapDb`)
- **CarMaker Integration**: TCP client for real-time vehicle control
- **Trigger System**: Condition-based action execution with state management

## Project Structure

### Frontend Structure (`src/`)

```
src/
├── routes/                          # SvelteKit routing
│   ├── +layout.svelte              # Main layout with sidebar
│   ├── +layout.ts                  # Layout load function
│   ├── +page.svelte                # Dashboard (main page)
│   │
│   ├── ai-settings/                # AI system configuration
│   │   ├── +layout.svelte          # Sub-sidebar layout
│   │   ├── +page.svelte            # Redirect to chat-settings
│   │   ├── +page.server.ts         # Server-side redirect
│   │   ├── chat-settings/+page.svelte    # Chat configuration
│   │   ├── system-messages/+page.svelte  # System message CRUD
│   │   ├── characters/+page.svelte       # Character CRUD
│   │   ├── commands/+page.svelte         # Command template CRUD
│   │   ├── user-info/+page.svelte        # User info management
│   │   └── final-message/+page.svelte    # Final message config
│   │
│   ├── map-settings/               # SUMO map management
│   │   ├── +layout.svelte          # Sub-sidebar layout
│   │   ├── +page.svelte            # Redirect to generator
│   │   ├── generator/+page.svelte  # Map creation/editing
│   │   ├── library/+page.svelte    # Map library with search
│   │   └── rag-test/+page.svelte   # RAG system testing
│   │
│   ├── autonomous-driving/         # CarMaker integration & vehicle control
│   │   ├── +layout.svelte          # Sub-sidebar layout
│   │   ├── +page.svelte            # Redirect to vehicle-control
│   │   ├── +page.server.ts         # Server-side redirect
│   │   ├── vehicle-control/+page.svelte  # Real-time vehicle control
│   │   ├── manual-control/+page.svelte   # Manual vehicle control
│   │   ├── triggers/+page.svelte         # Trigger management
│   │   └── settings/+page.svelte         # CarMaker settings
│   │
│   └── app-settings/+page.svelte   # Application settings
│
├── lib/                            # Shared library code
│   ├── components/                 # Svelte components
│   │   ├── TitleBar.svelte         # Custom titlebar with drag/controls
│   │   ├── Sidebar.svelte          # Collapsible navigation (14rem ↔ 5.5rem)
│   │   ├── Tooltip.svelte          # Fixed-position tooltips
│   │   ├── Dialog.svelte           # Generic dialog component
│   │   ├── HelpModal.svelte        # Help/documentation modal
│   │   ├── AIChatWidget.svelte     # AI chat widget (3 views)
│   │   ├── ChatView.svelte         # Chat interface with markdown
│   │   ├── ChatHistoryView.svelte  # Conversation history
│   │   ├── ChatSettingsView.svelte # Character/prompt selection
│   │   ├── MapCanvas.svelte        # SVG SUMO map visualization
│   │   └── MapCard.svelte          # Map display card
│   │
│   ├── stores/                     # Svelte stores
│   │   ├── uiStore.ts              # UI state (sidebar, chat, widget)
│   │   ├── dbWatcher.svelte.ts     # DB change detection (2s polling)
│   │   ├── settingsStore.ts        # App settings (minimize to tray)
│   │   ├── dialogStore.svelte.ts   # Dialog state management
│   │   ├── aiConfigStore.ts        # AI configuration state
│   │   ├── carmakerStore.svelte.ts # CarMaker connection & state
│   │   └── triggerMonitor.svelte.ts # Trigger monitoring & evaluation
│   │
│   ├── actions/                    # AI action processing
│   │   ├── parser.ts               # Tag parser (AI response → actions)
│   │   ├── executor.ts             # Action executor (invoke Tauri commands)
│   │   ├── formatter.ts            # Result formatter
│   │   ├── vehicleCommandParser.ts # Vehicle command parser
│   │   └── vehicleCommandExecutor.ts # Vehicle command executor
│   │
│   ├── utils/                      # Utility functions
│   │   └── triggerEvaluator.ts     # Trigger condition evaluator
│   │
│   ├── types/                      # TypeScript type definitions (empty)
│   ├── api/                        # API utilities (empty)
│   └── config.ts                   # App configuration
│
└── app.css                         # Global styles + Tailwind import
```

### Backend Structure (`src-tauri/src/`)

```
src-tauri/src/
├── main.rs                         # Tauri app entry point
├── lib.rs                          # Tauri command registration
│
├── commands/                       # Tauri commands (IPC handlers)
│   ├── mod.rs                      # Command exports
│   ├── ai_chat.rs                  # AI chat command (Claude CLI integration)
│   ├── conversations.rs            # Conversation CRUD
│   ├── characters.rs               # Character CRUD
│   ├── prompt_templates.rs         # System message CRUD
│   ├── command_templates.rs        # Command template CRUD
│   ├── maps.rs                     # SUMO map CRUD
│   ├── carmaker_control.rs         # CarMaker vehicle control commands
│   ├── triggers.rs                 # Trigger management commands
│   ├── settings.rs                 # App settings (minimize to tray, CarMaker)
│   ├── common.rs                   # Shared command utilities
│   └── utils.rs                    # Helper functions
│
├── db/                             # Database layer
│   ├── mod.rs                      # DB initialization (AiChatDb, MapDb wrappers)
│   ├── map_db.rs                   # SUMO maps database initialization
│   ├── schema.rs                   # Database schema definitions
│   ├── seed_data.rs                # Default data seeding
│   ├── sync.rs                     # Database sync utilities
│   │
│   └── models/                     # SeaORM entity models
│       ├── mod.rs                  # Model exports
│       ├── conversation.rs         # Conversation entity
│       ├── message.rs              # Message entity
│       ├── prompt_template.rs      # System message entity
│       ├── character.rs            # Character entity
│       ├── command_template.rs     # Command template entity
│       ├── map.rs                  # SUMO map entity
│       └── map_scenario.rs         # Map scenario entity
│
├── ai/                             # AI integration layer
│   ├── mod.rs                      # AI module exports
│   ├── claude_cli.rs               # Claude CLI subprocess manager
│   ├── prompt_builder.rs           # Dynamic prompt assembly
│   └── embeddings.rs               # OpenAI embeddings integration
│
├── carmaker/                       # CarMaker integration layer
│   ├── mod.rs                      # CarMaker module exports
│   ├── client.rs                   # CarMaker TCP client
│   └── types.rs                    # CarMaker data types
│
└── triggers/                       # Trigger system
    ├── mod.rs                      # Trigger module exports
    ├── state.rs                    # Trigger state management
    └── types.rs                    # Trigger data types
```

## Data Flow

### AI Chat Flow

```
User Input (Frontend)
    ↓
[1] invoke('chat', { request })
    ↓
[2] Rust backend (commands/ai_chat.rs)
    ├─ Load from database:
    │  ├─ System message (prompt_templates)
    │  ├─ Character prompt (characters)
    │  ├─ Active command templates (command_templates)
    │  └─ Conversation history (messages)
    ├─ Assemble CLAUDE.md + user message (prompt_builder.rs)
    └─ Execute Claude CLI subprocess (claude_cli.rs)
    ↓
[3] Claude CLI Response (raw text)
    ↓
[4] Frontend (actions/parser.ts)
    ├─ Parse action tags from response
    ├─ Execute READ actions first (actions/executor.ts)
    │  └─ invoke() Tauri commands → get data
    ├─ Feed results back to Claude (if needed)
    └─ Execute CUD actions (Create/Update/Delete)
       └─ invoke() Tauri commands → modify data
    ↓
[5] Save messages to database
    ↓
[6] UI auto-refresh (dbWatcher detects change)
```

### Database Auto-Refresh Flow

```
Frontend (dbWatcher.svelte.ts)
    ↓
[1] Poll every 2 seconds
    └─ invoke('get_db_timestamp')
    ↓
[2] Rust backend (commands/utils.rs)
    └─ Return SQLite file modification time
    ↓
[3] Frontend detects change
    ├─ Trigger onChange callbacks
    └─ Pages reload data automatically
```

### Map Management Flow

```
User Input (Generator/Library)
    ↓
[1] Create/Update/Delete Map
    └─ invoke('create_map' | 'update_map' | 'delete_map', { request })
    ↓
[2] Rust backend (commands/maps.rs)
    └─ Access MapDb wrapper (State<'_, MapDb>)
    └─ Execute SeaORM query on sumo_maps.db
    ↓
[3] Database auto-refresh triggers
    └─ dbWatcher detects change
    └─ Library page reloads map list
```

## Database Architecture

### Dual Database Pattern

The application uses **two separate SQLite databases** with wrapper types for type-safe state management:

```rust
// Wrapper types (src-tauri/src/db/mod.rs)
pub struct AiChatDb(pub DatabaseConnection);  // ai_chat.db
pub struct MapDb(pub DatabaseConnection);     // sumo_maps.db

// Tauri State registration (src-tauri/src/lib.rs)
.manage(AiChatDb(ai_chat_db))
.manage(MapDb(map_db))

// Commands use specific wrapper types
#[tauri::command]
pub async fn chat(request: ChatRequest, db: State<'_, AiChatDb>) -> Result<String, String>

#[tauri::command]
pub async fn create_map(request: CreateMapRequest, map_db: State<'_, MapDb>) -> Result<map::Model, String>
```

### AI Chat Database (`ai_chat.db`)

**Generic, reusable AI conversation system**:
- `prompt_templates` - System messages (AI behavior templates)
- `characters` - Character prompts (personality/tone)
- `command_templates` - Command definitions (tag formats, action instructions)
- `conversations` - Chat sessions (links character + prompt template)
- `messages` - Chat history (user/assistant messages)

### SUMO Maps Database (`sumo_maps.db`)

**Domain-specific autonomous driving data**:
- `maps` - SUMO traffic maps (node_xml, edge_xml, metadata, embeddings)
- `map_scenarios` - Map scenarios (map_id, drivers, vehicles, traffic_config)

### Design Philosophy

- **Generic AI Chat**: All conversation-related tables in `ai_chat.db` for portability
- **Domain Separation**: Domain-specific data in separate databases
- **Type Safety**: Wrapper types prevent database connection mix-ups
- **Reusability**: AI chat system can be reused across different projects

## State Management

### Frontend Stores

1. **uiStore.ts** - UI state management
   - Sidebar collapse state (main + sub)
   - Chat widget visibility
   - Widget mode (chat-only with window resize)
   - Current conversation ID and title

2. **dbWatcher.svelte.ts** - Database change detection
   - 2-second polling via Tauri invoke
   - onChange callbacks for data refresh
   - Automatic UI updates when DB changes

3. **settingsStore.ts** - Application settings
   - Minimize to tray preference
   - Persisted to localStorage

4. **dialogStore.svelte.ts** - Dialog management
   - Generic confirm/alert dialogs
   - Promise-based API

5. **aiConfigStore.ts** - AI configuration
   - Character and prompt template selection
   - Synced with chat settings

### Backend State

- **Tauri State** - Managed state with wrapper types
  - `AiChatDb` - AI chat database connection
  - `MapDb` - SUMO maps database connection
  - Type-safe access in Tauri commands

## Widget Mode

**Compact chat-only interface**:
- Activated via titlebar button
- Window resizes to 420x620px
- Moves to bottom-right corner
- Hides all UI except chat widget
- Close button exits app (prepared for tray support)
- Restore button returns to normal mode

**Implementation**:
- `uiStore.isWidgetMode` tracks state
- `+layout.svelte` handles window resize via Tauri API
- `AIChatWidget.svelte` adapts UI layout

## CarMaker Integration

**Feature**: Real-time vehicle control and monitoring with CarMaker simulation

**Architecture**:
- **TCP Client**: Rust-based TCP connection to CarMaker
- **Real-time Data**: Vehicle state monitoring (speed, acceleration, steering, position)
- **Vehicle Control**: Speed, acceleration, steering angle commands
- **Trigger System**: Condition-based action execution (e.g., "if speed > 50, then brake")

**Frontend Components** (`/autonomous-driving`):
- **Vehicle Control** - Real-time dashboard with AI-based control
- **Manual Control** - Direct vehicle command input
- **Triggers** - Create/manage condition-based actions
- **Settings** - CarMaker connection configuration

**Backend Structure**:
- **CarMaker Client** (`src-tauri/src/carmaker/client.rs`):
  - TCP socket connection management
  - Command sending (speed, acceleration, steering)
  - Real-time data streaming
  - Connection state monitoring

- **Trigger System** (`src-tauri/src/triggers/`):
  - Condition evaluation (mathematical expressions)
  - Action execution based on vehicle state
  - State persistence and management

**Stores**:
- **carmakerStore** - Connection status, vehicle state, real-time updates
- **triggerMonitor** - Active trigger monitoring and evaluation

**Data Flow**:
```
Frontend (vehicle-control page)
    ↓
[1] Connect to CarMaker
    └─ invoke('connect_carmaker', { host, port })
    ↓
[2] Rust backend (carmaker/client.rs)
    └─ Establish TCP connection
    └─ Start data streaming
    ↓
[3] Real-time data updates
    ├─ Vehicle state → Frontend (carmakerStore)
    ├─ Trigger evaluation (triggerMonitor)
    └─ Condition-based actions
    ↓
[4] Send vehicle commands
    └─ invoke('send_carmaker_command', { command, value })
    └─ TCP send to CarMaker
```

**Trigger System**:
- **Conditions**: Mathematical expressions (e.g., `speed > 50`, `acceleration < -2`)
- **Actions**: Vehicle commands (speed, acceleration, steering)
- **State Management**: Active/inactive triggers with persistence
- **Real-time Evaluation**: Continuous condition checking against vehicle state

## Naming Conventions

### Backend (Rust)
- **Tauri communication**: `#[serde(rename_all = "camelCase")]` on all structs
- **Database columns**: `snake_case` (SeaORM handles conversion)
- **Field names**: `conversationId`, `messageContent`, `createdAt` (in JSON)

### Frontend (TypeScript/Svelte)
- **All fields**: `camelCase` (JavaScript standard)
- **TypeScript interfaces**: `conversationId`, `messageContent`
- **Template access**: `{conversation.messageCount}`, `{message.content}`

### Migration Rule
- **Old code may use snake_case** - convert to camelCase when encountered
- **Always verify**: Interface definition AND template usage match camelCase

## Key Technologies

### Tailwind CSS v4
- **Import syntax**: `@import "tailwindcss";` (not `@tailwind` directives)
- **Plugin**: `@tailwindcss/vite` (no PostCSS)
- **Custom utilities**: Defined as plain CSS classes in `app.css`

### Svelte 5 Runes
- **State**: `$state` (replaces `let` with reactivity)
- **Derived**: `$derived` (replaces `$:` reactive statements)
- **Effects**: `$effect` (replaces `$:` for side effects)

### SeaORM
- **Database**: SQLite with async/await
- **Migrations**: Schema defined in `db/schema.rs`
- **Entities**: Auto-generated from schema
- **Conversion**: `snake_case` DB ↔ `camelCase` JSON via serde

## Security Considerations

- **Command injection**: All user inputs sanitized before subprocess execution
- **SQL injection**: SeaORM prevents via parameterized queries
- **File access**: Tauri restricts filesystem access via permissions
- **IPC validation**: All Tauri commands validate input types

## Performance Optimizations

- **DB polling**: 2-second interval (balance between responsiveness and CPU usage)
- **SVG rendering**: MapCanvas uses efficient SVG primitives
- **Lazy loading**: Pages load data on mount, not at app start
- **Selective refresh**: Only changed data reloads (via dbWatcher callbacks)

## Future Architecture Plans

### Phase 2: Embedding System
- OpenAI Embeddings API integration (`ai/embeddings.rs`)
- FAISS vector database for similarity search
- Embedding status in `maps` table

### Phase 3: RAG System
- Semantic search for SUMO maps
- Context-aware map recommendations
- RAG test page (`/map-settings/rag-test`)

---

**Last Updated**: 2025-11-22
**Project**: AGI Voice V2 - Autonomous Driving Research Application
