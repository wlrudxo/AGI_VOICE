# Frontend Design Cleanup Notes

Scope: Svelte frontend under `src/` (widgets, settings, map/autonomous-driving flows) and global styles in `src/app.css`.

## Key Findings (Updated: 2025-11-23)

### ✅ Completed
- **AI Settings 색상 통일 (7개 파일 완료)**: `ai-settings/+page.svelte`, `ai-settings/chat-settings/+page.svelte`, `ai-settings/system-messages/+page.svelte`, `ai-settings/characters/+page.svelte`, `ai-settings/commands/+page.svelte`, `ai-settings/user-info/+page.svelte`, `ai-settings/final-message/+page.svelte` - 모든 하드코딩 색상을 CSS 변수로 변환 완료
- **Map Settings 색상 통일 (3개 파일 완료)**: `map-settings/generator/+page.svelte`, `map-settings/library/+page.svelte`, `map-settings/rag-test/+page.svelte` - 모든 하드코딩 색상을 CSS 변수로 변환 완료
- **Autonomous-driving Settings 색상 통일 (4개 파일 완료)**: `autonomous-driving/settings/+page.svelte`, `autonomous-driving/vehicle-control/+page.svelte`, `autonomous-driving/manual-control/+page.svelte`, `autonomous-driving/triggers/+page.svelte` - 모든 하드코딩 색상을 CSS 변수로 변환 완료
### ✅ Completed
- **Form control 통일 (AI Settings 완료)**: AI Settings 7개 파일에서 `.input-field`, `.select-field`, `.textarea-field` 유틸리티 사용으로 통일 완료
- **Alert/message banners 통일 (AI Settings 완료)**: `ai-settings/chat-settings/+page.svelte`에서 `.alert-success`, `.alert-error` 유틸리티 사용으로 변경 완료
- **Badge 시스템 구축**: `.badge`, `.badge-success`, `.badge-error`, `.badge-info`, `.badge-warning` 유틸리티 app.css에 추가 완료
- **Button 통일 (AI Settings 완료)**: AI Settings 페이지에서 `.btn-icon` 사용으로 통일 완료
- **`.form-label` 수정**: display: flex로 변경하여 아이콘과 텍스트 가로 정렬 문제 해결

### ⏳ Remaining Issues
- Duplicate feature UI: chat settings exist both in `src/lib/components/ChatSettingsView.svelte` (widget) and the `ai-settings/chat-settings` page with near-identical fields and messages. Logic/UI divergence risk grows as one changes without the other.

## Light-Touch Unification Ideas (no over-abstraction)
- Replace hard-coded colors with semantic tokens or existing utility classes (`text-primary`, `bg-surface`, `border-default`) when touching those files; keeps palette coherent without introducing new helpers.
- Standardize on the global wrappers: use `card section` for panels and rely on the existing `page-header` style instead of redefining per page. If spacing differs, add a single modifier class in `app.css` (e.g., `.page-narrow`).
- Reuse the global form utilities: swap local input/select/textarea styles to `.input-field` / `.select-field`; add a `.textarea-field` variant in `app.css` if needed so per-page CSS can shrink.
- Centralize alerts/badges: add/extend `.alert-success|error|info|warning` and a small set of `.badge-{info,success,warning,neutral}` in `app.css`, then delete per-page duplicates. Triggers/map-library can share the badge tokens.
- Define one compact button variant (e.g., `.btn-compact`) in `app.css` instead of local `!important` overrides for control grids (vehicle-control, generator actions).
- Consider reusing the widget `ChatSettingsView` logic in `ai-settings/chat-settings` (or extract a small store/util) so default character/template/model handling stays in sync; avoids two validation/message flows.

## Progress Tracking

### ✅ Phase 1: Global Utilities (완료)
- [✅] Added `.textarea-field`, `.badge-*`, `.btn-compact`, `.form-label` (flex), `.loading-state`, `.empty-state` to `src/app.css`
- [✅] Added color variables: `--color-success-bg-light`, `--color-info-bg-light`, `--color-warning-bg-light`, etc.
- [✅] Added animation utilities: `@keyframes spin`, `.spin`, `pulse`, `fadeIn`, `slideInUp`

### ✅ Phase 2: AI Settings Migration (완료)
- [✅] Migrated all 7 AI settings pages to utilities
- [✅] Removed hard-coded colors from AI settings pages
- [✅] Unified form controls with `.input-field`, `.select-field`, `.textarea-field`
- [✅] Applied `.alert-*` utilities for message banners
- [✅] Code reduction: 289 lines removed across 7 files

### ✅ Phase 3: Map Settings Migration (완료)
- [✅] `map-settings/generator/+page.svelte`: Form 스타일 → 유틸리티 변경
- [✅] `map-settings/generator/+page.svelte`: `.message-box` → `.alert-*` 변경
- [✅] `map-settings/library/+page.svelte`: 하드코딩 색상 확인
- [✅] `map-settings/rag-test/+page.svelte`: 하드코딩 색상 (#f59e0b) 변환

### ✅ Phase 4: Autonomous-driving Settings Migration (완료)
- [✅] `autonomous-driving/settings/+page.svelte`: `.alert-*` 유틸리티 사용, 하드코딩 색상 제거
- [✅] `autonomous-driving/vehicle-control/+page.svelte`: `.btn-compact` 사용, `!important` 제거
- [✅] `autonomous-driving/manual-control/+page.svelte`: 중복 `.section` 스타일 제거
- [✅] `autonomous-driving/triggers/+page.svelte`: CSS 변수 변환, 중복 스타일 제거

### ⏳ Phase 5: Other Pages (대기)
- [ ] Consolidate chat settings UI/logic between `ChatSettingsView` and `/ai-settings/chat-settings`
- [ ] `ChatView.svelte`: `.empty-state` 유틸리티 사용, Scrollbar 중복 제거
- [ ] `settings/+page.svelte`: Tailwind-like 클래스명 제거
- [ ] `+page.svelte` (Dashboard): `.info-card` → `.card-interactive` 변경
- [ ] `HelpModal.svelte`: Dialog.svelte 컴포넌트로 통합 검토
- [ ] Sweep for lingering `#1f2937`/`#e5e7eb`/`#667eea` literals across all remaining files

## Current Status
- **Completed**: AI Settings 전체 (7개 파일), Map Settings 전체 (3개 파일), Autonomous-driving Settings 전체 (4개 파일)
- **Total Code Reduction**: ~425+ 줄
- **Pending**: Components (ChatView, HelpModal 등), Dashboard, Settings, Chat Settings 로직 통합, 전체 색상 최종 점검
