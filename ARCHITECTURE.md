# AI Diet V2 - Architecture Documentation

> Last Updated: 2025-10-18
> Status: Full Tauri Migration Complete

## Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [AI Integration System](#ai-integration-system)
6. [Frontend Architecture](#frontend-architecture)
7. [Backend Architecture](#backend-architecture)
8. [Key Features](#key-features)
9. [Development Guide](#development-guide)
10. [Common Issues & Solutions](#common-issues--solutions)

---

## Overview

AI Diet V2 is a desktop diet management application with AI-powered features built entirely on Tauri. The application provides:

- **Diet Tracking**: Record meals with nutritional information
- **Exercise Logging**: Track workouts with duration and calories
- **Weight Monitoring**: Daily weight tracking with visualization
- **AI Assistant**: Natural language interface for data entry and queries
- **Mission System**: AI-generated goals and tracking
- **Smart Evaluations**: Automated daily/weekly/monthly assessments

### Design Principles

1. **Date-based Design**: Uses `Date` type (YYYY-MM-DD) for user-facing dates to avoid timezone issues
2. **Dynamic Prompts**: Database-driven AI system with modular command templates
3. **Auto-refresh**: Real-time UI updates when backend modifies data
4. **Widget Mode**: Compact chat-only interface for quick interactions
5. **Frontend-Driven AI**: Two-pass AI system with frontend parsing and execution
6. **Full Tauri Architecture**: No separate backend server - Rust backend integrated in desktop app

---

## Technology Stack

### Frontend

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| Framework | SvelteKit | 2.9.0 | SSR/SSG framework |
| UI Library | Svelte | 5.0.0 | Reactive components with runes |
| Desktop | Tauri | 2.x | Rust-based desktop framework |
| Build Tool | Vite | 6.0.3 | Fast development server |
| Styling | Tailwind CSS | 4.1.14 | Utility-first CSS (v4 syntax) |
| Icons | Iconify | 5.0.2 | Solar duotone theme |
| Markdown | marked | 16.4.0 | Chat message rendering |

**Key Notes**:
- Svelte 5 uses **runes syntax**: `$state`, `$derived`, `$effect` (not `$:`)
- Tailwind v4 uses `@import "tailwindcss"` (not `@tailwind` directives)
- Tauri 2.x requires specific window permissions for custom titlebar

### Backend

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| Framework | Tauri | 2.x | Rust-based backend |
| Language | Rust | 1.70+ | Systems programming language |
| ORM | SeaORM | - | Async ORM for Rust |
| Database | SQLite | - | Local file-based database |
| AI Integration | Claude CLI | - | Subprocess-based Claude API |

**Key Notes**:
- All backend logic runs in Rust (no separate server process)
- Frontend communicates via Tauri `invoke()` commands
- Database file: `ai_diet.db` in project root
- Subprocess handling for Claude CLI built into Rust

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Tauri Desktop App                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              SvelteKit Frontend (Port 1420)           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │  │
│  │  │ Pages    │  │ Stores   │  │ Components       │   │  │
│  │  │ (Routes) │←→│ (State)  │←→│ (UI Elements)    │   │  │
│  │  └──────────┘  └──────────┘  └──────────────────┘   │  │
│  │       ↕                ↕                              │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │        AI Logic (Parser + Executor)          │   │  │
│  │  └──────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────┘  │
│                           ↕ Tauri invoke()                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Rust Backend (Tauri Commands)            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │  │
│  │  │ Commands │←→│ SeaORM   │←→│ Database (SQLite)│   │  │
│  │  └──────────┘  └──────────┘  └──────────────────┘   │  │
│  │       ↕                                               │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │    AI System (Prompt Builder + Claude CLI)   │   │  │
│  │  │  ┌──────────┐  ┌──────────┐                 │   │  │
│  │  │  │ Prompt   │→│ Claude   │                  │   │  │
│  │  │  │ Builder  │ │ CLI      │                  │   │  │
│  │  │  └──────────┘  └──────────┘                 │   │  │
│  │  └──────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

#### 1. User Input → AI Response (Frontend-Driven)

```
User Types Message
        ↓
Frontend (ChatView.svelte)
        ↓
invoke('chat', { request }) → Rust Backend
        ↓
Load: Character + Prompt Template + Commands + History (SeaORM)
        ↓
Build Dynamic Prompt (prompt_builder.rs)
        ↓
Save CLAUDE.md (temp file)
        ↓
Execute Claude CLI subprocess (claude_cli.rs)
        ↓
Return Raw Response to Frontend
        ↓
Frontend Parses Response Tags (parser.ts)
        ↓
Frontend Executes READ Actions → invoke() → Get Results
        ↓
Frontend Sends Results Back to Claude (Second Pass)
        ↓
Frontend Executes CUD Actions → invoke() → Update DB
        ↓
Update UI + Trigger DB Watcher
```

#### 2. Database Auto-Refresh

```
Rust Backend Modifies DB (via Tauri commands)
        ↓
SQLite File Modified Time Changes
        ↓
Frontend Polls get_db_timestamp (every 2s via invoke)
        ↓
Detects Timestamp Change
        ↓
Triggers Registered Callbacks
        ↓
Pages Reload Data Automatically (via invoke)
        ↓
UI Updates Without User Action
```

---

## Database Design

### Schema Overview

**9 Tables**:
- **3 Core Data Tables**: weights, meals, exercises
- **2 AI Mission Tables**: ai_missions, ai_evaluations
- **4 AI System Tables**: prompt_templates, characters, command_templates, conversations
- **1 Chat History Table**: messages

### Core Data Tables

#### `weights` - Weight Tracking

```sql
CREATE TABLE weights (
    id INTEGER PRIMARY KEY,
    measured_date DATE NOT NULL UNIQUE,  -- One weight per day
    weight REAL NOT NULL,                -- kg
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Key Points**:
- `measured_date` is unique (one record per day)
- Uses `Date` type (YYYY-MM-DD) to avoid timezone issues
- `created_at` is audit-only (not for user display)

#### `meals` - Meal Tracking

```sql
CREATE TABLE meals (
    id INTEGER PRIMARY KEY,
    meal_date DATE NOT NULL,              -- YYYY-MM-DD
    meal_type TEXT NOT NULL,              -- breakfast/lunch/dinner/snack/supplement
    food_name TEXT NOT NULL,
    calories INTEGER,
    protein REAL,
    carbs REAL,
    fat REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Key Points**:
- Multiple meals per day allowed
- `meal_type` values: breakfast, lunch, dinner, snack, supplement (영어/한글 모두 지원)
- Nutritional fields are optional

#### `exercises` - Exercise Tracking

```sql
CREATE TABLE exercises (
    id INTEGER PRIMARY KEY,
    exercise_date DATE NOT NULL,          -- YYYY-MM-DD
    exercise_name TEXT NOT NULL,
    duration INTEGER NOT NULL,            -- minutes
    calories INTEGER,
    category TEXT,                        -- 근력/유산소/etc.
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Key Points**:
- Multiple exercises per day allowed
- `duration` is required (minutes)
- `category` is freeform text

### AI System Tables

#### `prompt_templates` - System Messages

```sql
CREATE TABLE prompt_templates (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,                   -- Display name
    content TEXT NOT NULL,                -- System message content
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Core AI behavior instructions (e.g., "Diet Assistant System Message")

#### `characters` - AI Personalities

```sql
CREATE TABLE characters (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,                   -- Character name (e.g., "Aris")
    prompt_content TEXT NOT NULL,         -- Character personality/tone
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Define AI personality, tone, and speaking style

#### `command_templates` - Command Definitions

```sql
CREATE TABLE command_templates (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,                   -- Template name (e.g., "Meal Commands")
    content TEXT NOT NULL,                -- Command instructions
    is_active INTEGER DEFAULT 1,          -- 1=active, 0=inactive
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Modular tag-based CRUD instructions (only active templates sent to AI)

**Example Template**:
```markdown
## 식단 기록
<meal|name:음식명|calories:칼로리|meal_type:식사타입|date:날짜>

예시:
<meal|name:치킨|calories:2000|meal_type:lunch>
```

#### `conversations` - Chat Sessions

```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    character_id INTEGER NOT NULL,        -- FK to characters
    prompt_template_id INTEGER NOT NULL,  -- FK to prompt_templates
    user_info TEXT,                       -- User-specific context
    title TEXT,                           -- Conversation title
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Link character + prompt + user info for each chat session

#### `messages` - Chat History

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL,     -- FK to conversations
    role TEXT NOT NULL,                   -- user / assistant / system
    content TEXT NOT NULL,                -- Message content (with tags for assistant)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Store conversation history (includes system messages for READ results)

**Note**: Assistant messages store **original tags** for debugging

#### `ai_missions` - AI-Generated Goals

```sql
CREATE TABLE ai_missions (
    id INTEGER PRIMARY KEY,
    mission_title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,                 -- pending/in_progress/completed/failed
    ai_comment TEXT,
    completion_comment TEXT,
    deadline DATE,
    start_date DATETIME,                  -- Auto-set when status → in_progress
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Status Workflow**: pending → in_progress → completed/failed

#### `ai_evaluations` - Periodic Assessments

```sql
CREATE TABLE ai_evaluations (
    id INTEGER PRIMARY KEY,
    eval_type TEXT NOT NULL,              -- daily/weekly/monthly
    comment TEXT NOT NULL,                -- AI-generated evaluation
    author TEXT NOT NULL,                 -- Character name
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## AI Integration System

### Dynamic Prompt System

The AI uses a **database-driven dynamic prompt system** with variable substitution.

#### Prompt Assembly Flow

```
┌─────────────────────────────────────────────────────────┐
│                  CLAUDE.md (saved to temp file)          │
├─────────────────────────────────────────────────────────┤
│ ## System Message                                        │
│ [from prompt_templates table]                            │
│                                                           │
│ ## Character                                             │
│ [from characters table]                                  │
│                                                           │
│ ## User Information                                      │
│ [from conversation.user_info or request]                 │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│           User Message (sent to Claude CLI)              │
├─────────────────────────────────────────────────────────┤
│ ## 명령어 정보                                           │
│ [from command_templates where is_active=1]               │
│                                                           │
│ <--Previous Exchanges Start-->                           │
│ [conversation history from messages table]               │
│ <--Previous Response End-->                              │
│                                                           │
│ ## Current Input                                         │
│ [user input OR system context from READ results]         │
│ <--## Current Input End-->                               │
│                                                           │
│ ## Final Checkout                                        │
│ [custom checklist or default validation rules]           │
│                                                           │
│ ## Current Time                                          │
│ [YYYY년 M월 D일 요일 H시 M분]                            │
└─────────────────────────────────────────────────────────┘
```

#### Variable Substitution

Supports template variables:
- `{{user}}` → User name
- `{{char}}` → Character name

Example:
```
"안녕하세요 {{user}}님! 저는 {{char}}입니다."
→ "안녕하세요 선생님님! 저는 Aris입니다."
```

### Two-Pass System (Frontend-Driven)

#### Flow

1. **First Pass**: User input → Rust backend → Claude → Return raw response → Frontend parses → Execute READ actions
2. **Second Pass**: READ results → Send back to Rust → Claude → Return response → Frontend executes CUD actions

#### Example

**User Input**: "어제 먹은 거 알려줘"

**First Pass**:
```
Frontend → invoke('chat', { message: "어제 먹은 거 알려줘" })
        ↓
Rust → Claude: "<read_meal|date:2025-10-13> 어제 식단을 확인해볼게요!"
        ↓
Frontend parses tags → Executes READ via invoke('get_meals', { date: "2025-10-13" })
        ↓
Result: "어제 식단: 치킨 2000kcal, 샐러드 300kcal"
```

**Second Pass** (automatic):
```
Frontend → invoke('chat', { systemContext: "어제 식단: 치킨 2000kcal, 샐러드 300kcal" })
        ↓
Rust → Claude: "어제는 치킨과 샐러드를 드셨네요! 총 2300kcal 섭취하셨어요 😊"
        ↓
Frontend displays final response
```

### Tag System

All commands use unified tag format: `<type|field:value|field:value|...>`

#### CREATE Tags

```markdown
<meal|name:치킨|calories:2000|meal_type:lunch>
<exercise|name:런닝|duration:30|category:유산소>
<weight|weight:72.3|note:아침 체중>
<mission|name:운동 3회|description:이번 주 운동 3회 하기>
```

#### READ Tags

```markdown
<read_meal|date:2025-10-13>          # Specific date
<read_meal|id:5>                     # Specific record
<read_exercise|date:2025-10-13>
<read_weight|date:2025-10-13>
<read_mission|status:pending>        # By status
<read_dashboard>                     # Today
<read_dashboard|date:2025-10-13>    # Specific date
<read_dashboard|days:7>              # Last 7 days
```

#### UPDATE Tags

```markdown
<update_meal|id:5|calories:2500>
<update_exercise|id:3|duration:60>
<update_weight|id:1|weight:72.5|note:저녁 후>
<update_mission|id:2|status:completed>
```

#### DELETE Tags

```markdown
<delete_meal|id:5>                   # Delete by ID
<delete_meal|date:2025-10-13>       # Delete all meals on date
<delete_exercise|id:3>
<delete_weight|date:2025-10-13>
<delete_mission|id:2>
```

### Implementation Files

| File | Purpose |
|------|---------|
| `src-tauri/src/ai/prompt_builder.rs` | Assembles dynamic prompts + variable substitution |
| `src-tauri/src/ai/claude_cli.rs` | Manages Claude CLI subprocess |
| `src/lib/actions/parser.ts` | Parses response tags (Frontend) |
| `src/lib/actions/executor.ts` | Executes CRUD operations via invoke (Frontend) |
| `src-tauri/src/commands/ai_chat.rs` | Chat command with prompt assembly |

---

## Frontend Architecture

### Directory Structure

```
src/
├── routes/
│   ├── +layout.svelte              # Main layout with sidebar + titlebar
│   ├── +page.svelte                # Dashboard
│   ├── meals/+page.svelte          # Meal management
│   ├── exercises/+page.svelte      # Exercise management
│   ├── weights/+page.svelte        # Weight tracking
│   ├── missions/+page.svelte       # AI missions
│   ├── settings/+page.svelte       # Application settings
│   └── ai-settings/                # AI system configuration
│       ├── +layout.svelte          # Sub-sidebar layout
│       ├── chat-settings/+page.svelte
│       ├── system-messages/+page.svelte
│       ├── characters/+page.svelte
│       ├── commands/+page.svelte
│       ├── user-info/+page.svelte
│       └── final-message/+page.svelte
├── lib/
│   ├── components/
│   │   ├── TitleBar.svelte         # Custom titlebar with drag + controls
│   │   ├── Sidebar.svelte          # Collapsible navigation
│   │   ├── Tooltip.svelte          # Fixed-position tooltips
│   │   ├── AIChatWidget.svelte     # AI chat widget with dual views
│   │   ├── ChatView.svelte         # Chat interface with markdown
│   │   ├── ChatHistoryView.svelte  # Conversation list
│   │   └── ChatSettingsView.svelte # Character/prompt selection modal
│   ├── stores/
│   │   ├── uiStore.ts              # UI state (sidebar, chat, widget mode)
│   │   ├── dbWatcher.svelte.ts     # DB change detection (2s polling)
│   │   ├── settingsStore.ts        # App settings (minimize to tray, etc)
│   │   └── weights.svelte.ts       # Weight data store (example)
│   └── actions/
│       ├── parser.ts               # Tag parser for AI responses
│       ├── executor.ts             # Action executor via Tauri invoke
│       └── formatter.ts            # Result formatter
└── app.css                         # Global styles with Tailwind import
```

### State Management

#### `uiStore.ts` - UI State

```typescript
interface UiState {
  isSidebarCollapsed: boolean;
  isChatOpen: boolean;
  chatViewMode: 'chat' | 'history';
  currentConversationId: number | null;
  currentConversationTitle: string | null;
  isWidgetMode: boolean;
  wasWidgetModeBeforeTray: boolean;  // For tray → restore flow
}
```

**Methods**:
- `toggleSidebar()`, `setSidebarCollapsed()`
- `toggleChat()`, `setChatOpen()`
- `setChatViewMode(mode)` - Switch between chat/history views
- `setCurrentConversationId(id)` - Track active conversation
- `setCurrentConversationTitle(title)` - Display in widget header
- `setWidgetMode(isWidget)` - Enter/exit widget mode
- `saveWidgetModeBeforeTray()`, `restoreModeFromTray()` - Tray flow helpers

**Persistence**: Saves to `localStorage`:
- `ai_diet_chat_view_mode`
- `ai_diet_conversation_id`
- `ai_diet_conversation_title`
- `ai_diet_was_widget_mode_before_tray`

#### `settingsStore.ts` - App Settings

```typescript
interface AppSettings {
  minimizeToTray: boolean;
}
```

**Methods**:
- `setMinimizeToTray(value)` - Enable/disable minimize to tray
- `loadSettings()` - Reload from localStorage

**Persistence**: Saves to `localStorage`:
- `ai_diet_app_settings`

#### `dbWatcher.svelte.ts` - Auto-Refresh

```typescript
interface DbState {
  lastTimestamp: number | null;
  isWatching: boolean;
}
```

**Methods**:
- `startWatching()` - Begin polling `get_db_timestamp` every 2s via invoke
- `stopWatching()` - Stop polling
- `onChange(callback)` - Register callback for DB changes (returns unsubscribe function)
- `triggerRefresh(delay)` - Manually trigger refresh (for immediate feedback)

**Usage Pattern**:
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

### Key Components

#### `TitleBar.svelte` - Custom Titlebar

**Features**:
- Drag area for window movement
- Window controls (minimize, maximize, close)
- Double-click to maximize
- Widget mode button
- System tray button (prepared)

**Tauri Permissions Required**:
```json
"core:window:allow-start-dragging",
"core:window:allow-minimize",
"core:window:allow-maximize",
"core:window:allow-close",
"core:window:allow-toggle-maximize",
"core:window:allow-internal-toggle-maximize"
```

#### `ChatView.svelte` - Chat Interface

**Features**:
- Message list with markdown rendering (marked.js)
- Input area with send button
- Auto-scroll to bottom
- Message count display
- Settings button (character/prompt selection)

**Integration**:
- Uses `invoke('chat', { request })` to send messages
- Parses response tags in frontend
- Executes actions via separate invoke calls
- Displays action indicators (e.g., "📋 식단 1개 추가됨")

---

## Backend Architecture

### Directory Structure

```
src-tauri/
├── src/
│   ├── main.rs                      # Tauri app entry point
│   ├── lib.rs                       # Command registration
│   ├── commands/
│   │   ├── mod.rs                   # Command module exports
│   │   ├── meals.rs                 # Meal CRUD commands
│   │   ├── exercises.rs             # Exercise CRUD commands
│   │   ├── weights.rs               # Weight CRUD commands
│   │   ├── missions.rs              # Mission CRUD commands
│   │   ├── dashboard.rs             # Dashboard aggregation
│   │   ├── ai_chat.rs               # AI chat command
│   │   ├── settings.rs              # Settings + DB timestamp
│   │   ├── prompt_templates.rs      # System message CRUD
│   │   ├── characters.rs            # Character CRUD
│   │   ├── command_templates.rs     # Command template CRUD
│   │   └── conversations.rs         # Conversation + message CRUD
│   ├── db/
│   │   ├── mod.rs                   # Database initialization
│   │   ├── models/
│   │   │   ├── mod.rs               # Model exports
│   │   │   ├── weight.rs            # Weight entity
│   │   │   ├── meal.rs              # Meal entity
│   │   │   ├── exercise.rs          # Exercise entity
│   │   │   ├── ai_mission.rs        # Mission entity
│   │   │   ├── prompt_template.rs   # System message entity
│   │   │   ├── character.rs         # Character entity
│   │   │   ├── command_template.rs  # Command template entity
│   │   │   ├── conversation.rs      # Conversation entity
│   │   │   └── message.rs           # Message entity
│   │   └── sync.rs                  # Database sync utilities (prepared)
│   └── ai/
│       ├── mod.rs                   # AI module exports
│       ├── claude_cli.rs            # Claude CLI subprocess manager
│       └── prompt_builder.rs        # Dynamic prompt assembly
├── Cargo.toml                       # Rust dependencies
└── tauri.conf.json                  # Tauri configuration
```

### Tauri Commands

All frontend-backend communication uses Tauri `invoke()` commands:

#### Data CRUD Commands

```rust
// Meals
#[tauri::command]
async fn get_meals(meal_date: String) -> Result<Vec<Meal>, String>
#[tauri::command]
async fn create_meal(meal: CreateMealRequest) -> Result<Meal, String>
#[tauri::command]
async fn update_meal(id: i32, meal: UpdateMealRequest) -> Result<Meal, String>
#[tauri::command]
async fn delete_meal(id: i32) -> Result<(), String>

// Exercises (similar pattern)
// Weights (similar pattern)
// Missions (similar pattern)
```

#### AI System Commands

```rust
#[tauri::command]
async fn chat(request: ChatRequest) -> Result<ChatResponse, String>

#[tauri::command]
async fn get_conversations() -> Result<Vec<ConversationWithCount>, String>

#[tauri::command]
async fn get_conversation_messages(id: i32, limit: Option<i32>) -> Result<Vec<Message>, String>

#[tauri::command]
async fn get_characters() -> Result<Vec<Character>, String>

#[tauri::command]
async fn get_prompt_templates() -> Result<Vec<PromptTemplate>, String>

#[tauri::command]
async fn get_command_templates() -> Result<Vec<CommandTemplate>, String>

#[tauri::command]
async fn toggle_command_template(id: i32) -> Result<CommandTemplate, String>
```

#### Utility Commands

```rust
#[tauri::command]
async fn get_db_timestamp() -> Result<DbTimestamp, String>

#[tauri::command]
async fn get_dashboard(target_date: String) -> Result<DashboardData, String>

#[tauri::command]
async fn get_weekly_dashboard(days: i32) -> Result<WeeklyDashboard, String>

#[tauri::command]
async fn get_chat_settings() -> Result<ChatSettings, String>
```

### AI Chat Command (`chat`)

**Request**:
```rust
#[derive(Deserialize)]
struct ChatRequest {
    conversation_id: Option<i32>,
    character_id: Option<i32>,
    prompt_template_id: Option<i32>,
    user_info: Option<String>,
    user_name: Option<String>,
    final_message: Option<String>,
    title: Option<String>,
    message: String,
    model: String,  // sonnet/haiku/opus
    system_context: Option<String>,  // For second pass
}
```

**Response**:
```rust
#[derive(Serialize)]
struct ChatResponse {
    conversation_id: i32,
    responses: Vec<String>,  // Raw responses from Claude
}
```

**Implementation Flow**:
1. Load conversation (or create new)
2. Load character, prompt template, active command templates
3. Load conversation history
4. Build CLAUDE.md (prompt_builder.rs)
5. Build user message with commands + history + current input
6. Execute Claude CLI subprocess (claude_cli.rs)
7. Save user message + assistant response to DB
8. Return raw response to frontend
9. Frontend handles parsing and execution

---

## Key Features

### 1. Widget Mode

**Purpose**: Compact chat-only interface for quick interactions

**Activation**:
- Click widget button in titlebar
- Window resizes to 420x620px
- Moves to bottom-right corner of screen
- All UI except chat widget hidden

**UI Changes**:
- Sidebar hidden
- Main content hidden
- Only chat widget visible
- Widget header shows conversation title
- Close button exits app (for future tray mode)

**Implementation**:
```typescript
// +layout.svelte
if (isWidgetMode) {
  await appWindow.setSize(new LogicalSize(420, 620));
  const monitor = await appWindow.currentMonitor();
  if (monitor) {
    const x = monitor.size.width - 440;
    const y = monitor.size.height - 640;
    await appWindow.setPosition(new LogicalPosition(x, y));
  }
}
```

### 2. System Tray (Ready)

**Status**: Tauri permissions configured, implementation prepared

**Features**:
- Minimize to tray (hide window)
- Show from tray (restore previous state)
- Restores widget mode if previously active
- Tray icon + menu + tooltip

**Permissions**:
```json
"core:tray:allow-new",
"core:tray:allow-set-icon",
"core:tray:allow-set-menu",
"core:tray:allow-set-tooltip"
```

### 3. Database Auto-Refresh

**Problem**: User doesn't see changes made by AI

**Solution**: Frontend polls DB timestamp every 2 seconds

**Backend** (Rust command):
```rust
#[tauri::command]
fn get_db_timestamp() -> Result<DbTimestamp, String> {
    let db_path = "../ai_diet.db";
    let metadata = fs::metadata(db_path)?;
    let mtime = metadata.modified()?.duration_since(UNIX_EPOCH)?.as_secs();
    Ok(DbTimestamp { unix_timestamp: mtime })
}
```

**Frontend** (`dbWatcher.svelte.ts`):
```typescript
// Poll every 2 seconds via invoke
setInterval(async () => {
  const { unix_timestamp } = await invoke('get_db_timestamp');
  if (unix_timestamp !== lastTimestamp) {
    callbacks.forEach(cb => cb());
  }
}, 2000);
```

### 4. Frontend-Driven AI System

**Architecture**: AI response parsing and action execution moved to frontend

**Benefits**:
- Clearer separation of concerns
- Easier debugging (can inspect tags in browser)
- More flexible (can add new action types without backend changes)
- Better error handling

**Flow**:
```typescript
// 1. Send message
const data = await invoke('chat', { request });
const rawResponse = data.responses[0];

// 2. Parse tags (Frontend)
const actions = parseActions(rawResponse);

// 3. Execute READ actions
const readResults = await executeActions(readActions);

// 4. Send results back to Claude
const followupData = await invoke('chat', {
  systemContext: formatReadResults(readResults)
});

// 5. Execute CUD actions
await executeActions(cudActions);
```

### 5. Dynamic Prompt System

**Components**:
1. **System Message** (prompt_templates): Core behavior
2. **Character** (characters): Personality/tone
3. **Command Templates** (command_templates): Modular commands
4. **User Info**: User context
5. **Final Message**: Custom validation rules

**Activation System**:
- Each command template has `is_active` field
- Only active templates sent to AI
- Allows turning features on/off without deletion

**Variable Substitution**:
- `{{user}}` → User name
- `{{char}}` → Character name
- Applied to all prompt components

---

## Development Guide

### Prerequisites

**Frontend**:
- Node.js 18+ (for Vite 6.x)
- npm or pnpm

**Backend**:
- Rust 1.70+ (for Tauri 2.x)
- C++ build tools (Windows)

**AI**:
- Claude CLI installed globally

### Initial Setup

```bash
# 1. Clone repository
git clone <repo_url>
cd AI_Diet_V2

# 2. Install frontend dependencies
npm install

# 3. Install Tauri CLI (if not installed)
npm install -g @tauri-apps/cli

# 4. Build Rust dependencies (first time only)
cd src-tauri
cargo build
cd ..
```

### Running Development Server

```bash
# Development mode (hot reload)
npm run tauri dev

# Or use start.bat on Windows
start.bat
```

### Building for Production

```bash
# Build desktop app
npm run tauri build

# Output: src-tauri/target/release/bundle/
# - .exe installer (Windows)
# - .app bundle (macOS)
# - .deb/.AppImage (Linux)
```

### Database Management

**Location**: `ai_diet.db` in project root

**Inspect Database**:
```bash
sqlite3 ai_diet.db
.tables
SELECT * FROM conversations;
.exit
```

**Note**: Database is created automatically on first run with seed data

### Testing AI System

**Test via Application**:
1. Run `npm run tauri dev`
2. Open AI chat widget
3. Configure character/prompt in settings
4. Send test messages

**Test Prompt Builder** (Rust):
```bash
cd src-tauri
cargo test
```

---

## Common Issues & Solutions

### Issue 1: Database Connection Errors

**Error**: Database file not found

**Solution**: Ensure `ai_diet.db` exists in project root. Tauri creates it automatically on first run.

### Issue 2: Command Templates Not Working

**Symptom**: AI doesn't use tags despite commands configured

**Cause**: All templates are deactivated (`is_active=0`)

**Solution**:
1. Go to `/ai-settings/commands`
2. Find template
3. Click toggle button to activate (green = active)

### Issue 3: Widget Mode Not Resizing

**Symptom**: Window doesn't resize when entering widget mode

**Cause**: Missing Tauri window permissions

**Solution**: Check `tauri.conf.json` includes:
```json
"core:window:allow-set-size",
"core:window:allow-set-position"
```

### Issue 4: Auto-Refresh Not Working

**Symptom**: UI doesn't update after AI modifies data

**Debugging**:
1. Check browser console for errors
2. Verify `dbWatcher.startWatching()` called in page
3. Check `invoke('get_db_timestamp')` returns valid timestamp

**Common Fix**: Forgot to call `startWatching()` in `onMount()`

### Issue 5: Claude CLI Not Found

**Error**: `claude` executable not found

**Solution**:
```bash
# Install Claude CLI globally
npm install -g @anthropic-ai/claude-cli

# Verify installation
claude --version
```

### Issue 6: Tauri Build Errors

**Error**: Rust compilation errors

**Solution**:
```bash
# Update Rust
rustup update

# Clean build cache
cd src-tauri
cargo clean
cargo build
```

### Issue 7: Svelte 5 Syntax Errors

**Error**: `$ is not defined`

**Cause**: Using old Svelte 3/4 syntax

**Fix**: Use runes:
```svelte
<!-- OLD -->
$: count = value * 2;

<!-- NEW (Svelte 5) -->
let count = $derived(value * 2);
```

---

## Next Steps (Future Development)

### Phase 4: System Tray Integration
- [ ] Activate tray implementation
- [ ] Test minimize/restore flow
- [ ] Add tray menu items
- [ ] Handle tray click events

### Phase 5: Data Visualization
- [ ] Weight chart with trend lines
- [ ] Calorie intake/burn charts
- [ ] Weekly/monthly summaries
- [ ] Goal progress indicators

### Phase 6: Advanced AI Features
- [ ] Custom evaluation schedules
- [ ] Multi-character support
- [ ] Voice input/output
- [ ] Image recognition for food logging

### Phase 7: Cloud Sync
- [ ] Optional cloud backup
- [ ] Multi-device sync
- [ ] Export/import data

---

## Conclusion

AI Diet V2 is a fully integrated Tauri desktop application with a powerful frontend-driven AI system. The architecture prioritizes:

1. **Developer Experience**: Clear separation of concerns, easy to extend
2. **User Experience**: Real-time updates, smooth interactions, compact widget mode
3. **Flexibility**: Database-driven prompts, modular commands, variable substitution
4. **Performance**: Native Rust backend, no separate server process
5. **Reliability**: Two-pass AI system, auto-refresh, proper error handling

For questions or contributions, see project repository or contact maintainers.

---

**Document Version**: 2.0
**Last Updated**: 2025-10-18
**Maintainer**: AI Diet V2 Team
