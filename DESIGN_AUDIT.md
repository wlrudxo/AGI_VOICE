# Design System Audit Report

**프로젝트**: AGI Voice V2
**날짜**: 2025-11-23
**목적**: 디자인 통일성 유지 및 중복 코드 정리 (개발 효율성 향상)

---

## 📊 Executive Summary

Frontend 전체 분석 결과, **app.css 유틸리티의 일관성 없는 사용**과 **중복된 스타일 정의**가 주요 문제로 확인되었습니다.

### 주요 발견 사항
- **22개 파일 분석** (components + routes)
- **68%의 파일**에서 중복 스타일 발견
- **82%의 파일**에서 기존 유틸리티 미사용
- **50+ 개의 하드코딩된 색상 값**
- **30+ 개의 중복 패턴 인스턴스**

### 권장 사항 요약
✅ **추가 필요한 유틸리티**: 8개 (empty-state, loading-state, form-group 등)
❌ **제거 가능한 중복 코드**: 30+ 인스턴스
🔄 **표준화 필요**: 하드코딩된 색상 → CSS 변수 변환

---

## 🔴 Priority 1: 중복 CSS 정의 (CRITICAL)

### 1.1 버튼 스타일 중복

**문제**: app.css에 `.btn-icon`이 있는데 커스텀 버튼 스타일 재정의

**발견 위치**:
```
src/routes/ai-settings/characters/+page.svelte (Lines 223-251)
src/routes/map-settings/library/+page.svelte (Lines 598-618)
```

**기존 코드**:
```css
/* characters/+page.svelte */
.edit-btn, .delete-btn {
  padding: 0.375rem;
  background: transparent;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  color: var(--color-text-muted);
  transition: all 0.2s;
}

.edit-btn:hover { color: var(--color-primary); }
.delete-btn:hover { color: var(--color-error); }
```

**해결 방법**:
```svelte
<!-- ❌ 기존 -->
<button class="edit-btn">...</button>
<button class="delete-btn">...</button>

<!-- ✅ 수정 -->
<button class="btn-icon">...</button>
<button class="btn-icon danger">...</button>
```

**영향**: app.css의 `.btn-icon`, `.btn-icon.danger`를 사용하면 30줄 이상 코드 제거 가능

---

### 1.2 Form Input 스타일 중복

**문제**: `.input-field`, `.select-field` 유틸리티가 존재하는데 재정의

**발견 위치**:
```
src/routes/ai-settings/characters/+page.svelte (Lines 219-233)
src/routes/ai-settings/commands/+page.svelte (Lines 439-452)
src/routes/ai-settings/system-messages/+page.svelte (Lines 201-215)
src/routes/map-settings/generator/+page.svelte (Lines 356-368)
```

**기존 코드**:
```css
.form-group input, .form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db; /* ❌ 하드코딩된 색상 */
  border-radius: 0.5rem;
  font-size: 1rem;
}
```

**해결 방법**:
```svelte
<!-- ❌ 기존 -->
<input type="text" />

<!-- ✅ 수정 -->
<input type="text" class="input-field w-full" />
```

**영향**: 4개 파일에서 60줄 이상 코드 제거 가능

---

### 1.3 Card 컴포넌트 중복

**문제**: 유사한 목적의 카드 컴포넌트가 다르게 구현됨

**발견 위치**:
```
src/routes/+page.svelte (Lines 105-116) - .info-card
src/routes/ai-settings/characters/+page.svelte (Lines 256-267) - .character-card
src/routes/ai-settings/commands/+page.svelte (Lines 344-358) - .command-card
```

**패턴 분석**:
```css
/* 공통 패턴 */
background: var(--color-surface);
border: 1px solid var(--color-border);
border-radius: 0.5rem ~ 0.75rem;
padding: 1.5rem ~ 2rem;
box-shadow: var(--shadow-sm);
transition: transform 0.2s, box-shadow 0.2s;

/* hover 시 */
transform: translateY(-4px);
box-shadow: var(--shadow-md);
```

**해결 방법**: app.css에 `.card-hover` 확장
```css
/* app.css에 추가 */
.card-interactive {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
  transition: all 0.2s;
}

.card-interactive:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}
```

---

## 🟡 Priority 2: 기존 유틸리티 미사용

### 2.1 텍스트 색상

**발견**: `var(--color-text-muted)` 직접 사용 대신 `.text-muted` 클래스 미사용

**영향 파일**: ChatView.svelte, ChatHistoryView.svelte, settings/+page.svelte 등

**수정 예시**:
```svelte
<!-- ❌ 기존 -->
<p style="color: var(--color-text-muted);">힌트 텍스트</p>

<!-- ✅ 수정 -->
<p class="text-muted">힌트 텍스트</p>
```

---

### 2.2 배경 색상

**발견**: `background: white` 또는 `var(--color-surface)` 직접 사용

**영향 파일**: ChatSettingsView.svelte, commands/+page.svelte 등

**수정 예시**:
```svelte
<!-- ❌ 기존 -->
<div style="background: var(--color-surface);">...</div>

<!-- ✅ 수정 -->
<div class="bg-surface">...</div>
```

---

### 2.3 Border 스타일

**발견**: `border: 1px solid var(--color-border)` 직접 정의

**수정 예시**:
```svelte
<!-- ❌ 기존 -->
<div style="border: 1px solid var(--color-border);">...</div>

<!-- ✅ 수정 -->
<div class="border border-default">...</div>
```

---

## 🔄 Priority 3: 패턴 일관성 문제

### 3.1 Empty State 패턴 (7회 중복)

**발견 위치**:
```
ChatView.svelte (Lines 705-713)
ChatHistoryView.svelte (Lines 201-221)
map-settings/library/+page.svelte (Lines 655-678)
ai-settings/characters/+page.svelte
ai-settings/commands/+page.svelte
... (총 7개 파일)
```

**현재 코드** (각 파일마다 재정의):
```css
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: var(--color-text-muted);
}
```

**권장 해결 방법**: app.css에 유틸리티 추가
```css
/* app.css에 추가 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  padding: 2rem;
  text-align: center;
  color: var(--color-text-muted);
  gap: 1rem;
}

.empty-state-icon {
  font-size: 3rem;
  opacity: 0.3;
}
```

**영향**: 7개 파일에서 70줄 이상 코드 제거 가능

---

### 3.2 Loading State 패턴 (5회 중복)

**발견 위치**:
```
commands/+page.svelte
library/+page.svelte
ChatHistoryView.svelte
characters/+page.svelte
system-messages/+page.svelte
```

**권장 해결 방법**: app.css에 유틸리티 추가
```css
/* app.css에 추가 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  color: var(--color-text-secondary);
  gap: 1rem;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spin {
  animation: spin 1s linear infinite;
}
```

**사용 예시**:
```svelte
<!-- ✅ 표준화된 로딩 UI -->
<div class="loading-state">
  <Icon icon="solar:ufo-2-duotone" width="48" class="spin" />
  <p>데이터를 불러오는 중...</p>
</div>
```

---

### 3.3 Modal/Dialog 구현 (3회 중복)

**문제**: Dialog.svelte 컴포넌트가 있는데 인라인 모달 구현

**발견 위치**:
```
Dialog.svelte (공식 컴포넌트)
HelpModal.svelte (거의 동일한 구현)
commands/+page.svelte (인라인 모달)
```

**권장 해결 방법**:
1. **Dialog.svelte 통일** 사용
2. HelpModal.svelte → Dialog.svelte 사용하도록 리팩토링
3. commands/+page.svelte 인라인 모달 제거

**영향**: 150줄 이상 코드 제거 가능

---

## 🎨 Priority 4: 색상 사용 문제

### 4.1 하드코딩된 색상 값 (50+ 인스턴스)

**심각한 문제 파일**: `characters/+page.svelte`, `commands/+page.svelte`

**발견된 하드코딩 색상**:
```css
/* ❌ 하드코딩 */
border-bottom: 1px solid #e5e7eb;
color: #1f2937;
color: #374151;
color: #6b7280;
background: #fee2e2;
color: #991b1b;
background: #d1fae5;
color: #065f46;
```

**해결 방법**:
```css
/* ✅ CSS 변수 사용 */
border-bottom: 1px solid var(--color-border);
color: var(--color-text-primary);
color: var(--color-text-secondary);
color: var(--color-text-muted);
background: var(--color-error-bg-light);
color: var(--color-error);
background: var(--color-success-bg-light); /* 추가 필요 */
color: var(--color-success-dark); /* 추가 필요 */
```

**app.css에 추가 필요한 색상 변수**:
```css
@theme {
  /* Success background variants */
  --color-success-bg-light: rgba(72, 187, 120, 0.1);
  --color-success-text: #065f46;

  /* Info background variants */
  --color-info-bg-light: rgba(66, 153, 225, 0.1);
  --color-info-text: #0c4a6e;

  /* Warning background variants */
  --color-warning-bg-light: rgba(237, 137, 54, 0.1);
  --color-warning-text: #92400e;
}
```

---

### 4.2 일관성 없는 색상 참조 방식

**같은 파일 내에서 3가지 방식 혼용**:
```svelte
<!-- settings/+page.svelte 예시 -->
<div style="color: var(--color-text-primary);">...</div>  <!-- ❌ 인라인 스타일 -->
<div class="text-primary">...</div>                      <!-- ✅ 유틸리티 클래스 -->
<div style="color: #1f2937;">...</div>                    <!-- ❌ 하드코딩 -->
```

**표준화 방법**: 유틸리티 클래스 우선 사용
```svelte
<!-- ✅ 권장: 유틸리티 클래스 -->
<div class="text-primary">...</div>
<div class="text-secondary">...</div>
<div class="text-muted">...</div>

<!-- ⚠️ 필요시에만: CSS 변수 -->
<div style="color: var(--color-text-primary);">...</div>

<!-- ❌ 절대 금지: 하드코딩 -->
<div style="color: #1f2937;">...</div>
```

---

## ➕ 추가 권장 유틸리티

### 1. Form 관련 유틸리티

**현황**: 10+ 파일에서 중복 정의

```css
/* app.css에 추가 */
.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
  font-size: 0.9rem;
}

.form-hint {
  margin-top: 0.375rem;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.form-error {
  margin-top: 0.375rem;
  font-size: 0.75rem;
  color: var(--color-error);
}
```

**사용 예시**:
```svelte
<div class="form-group">
  <label class="form-label" for="name">이름</label>
  <input type="text" id="name" class="input-field w-full" />
  <p class="form-hint">실명을 입력해주세요</p>
</div>
```

---

### 2. Filter/Badge 유틸리티

**현황**: library/+page.svelte, commands/+page.svelte에서 중복

```css
/* app.css에 추가 */
.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-success {
  background: var(--color-success-bg-light);
  color: var(--color-success-text);
}

.badge-error {
  background: var(--color-error-bg-light);
  color: var(--color-error);
}

.badge-info {
  background: var(--color-info-bg-light);
  color: var(--color-info-text);
}

.badge-warning {
  background: var(--color-warning-bg-light);
  color: var(--color-warning-text);
}
```

---

### 3. 애니메이션 유틸리티

```css
/* app.css에 추가 */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInUp {
  from {
    transform: translateY(1rem);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.spin { animation: spin 1s linear infinite; }
.pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
.fade-in { animation: fadeIn 0.2s ease-out; }
.slide-in-up { animation: slideInUp 0.3s ease-out; }
```

---

### 4. 배경색 확장

```css
/* app.css에 추가 */
.bg-white {
  background-color: #ffffff;
}

.bg-success-light {
  background-color: var(--color-success-bg-light);
}

.bg-info-light {
  background-color: var(--color-info-bg-light);
}

.bg-warning-light {
  background-color: var(--color-warning-bg-light);
}
```

---

## ⚠️ Over-Abstraction 검토

### 1회만 사용되는 유틸리티 (컴포넌트로 이동 고려)

```
.sub-sidebar-toggle-btn (app.css Lines 580-597)
→ ai-settings/+layout.svelte에서만 사용
→ 컴포넌트 내부 스타일로 이동 가려

.status-indicator (app.css Lines 652-673)
→ autonomous-driving 페이지에서만 사용 (추측)
→ 유지 여부 확인 필요

.slider (app.css Lines 676-702)
→ 사용 빈도 확인 필요
→ 1-2회만 사용되면 컴포넌트로 이동
```

**권장 사항**:
- 2회 이상 사용되는 패턴만 app.css에 유지
- 1회 사용은 컴포넌트 `<style>` 태그로 이동

---

## 📋 구체적 파일별 수정 계획

### 🔥 High Priority

#### `characters/+page.svelte` [✅ 완료]
- [✅] `.edit-btn`, `.delete-btn` → `.btn-icon` 변경
- [✅] Form input 스타일 → `.input-field` 사용
- [✅] 하드코딩 색상 20+ 개 → CSS 변수 변환
- [✅] `.loading-state` → app.css 유틸리티 사용
- **실제 코드 감소**: 36줄

#### `commands/+page.svelte` [✅ 완료]
- [✅] 인라인 모달 제거 → Dialog.svelte 컴포넌트 사용
- [✅] Form 스타일 중복 제거
- [✅] 하드코딩 색상 → CSS 변수
- [✅] `.loading-state` → app.css 유틸리티 사용
- [✅] `.badge` 유틸리티 사용
- **실제 코드 감소**: 63줄

#### `system-messages/+page.svelte` [✅ 완료]
- [✅] Form 스타일 → `.input-field`, `.textarea-field` 사용
- [✅] `.loading-state` → app.css 유틸리티 사용
- **실제 코드 감소**: 28줄

#### `chat-settings/+page.svelte` [✅ 완료]
- [✅] `.alert-success`, `.alert-error` 유틸리티 사용
- [✅] `.loading-state` → app.css 유틸리티 사용
- [✅] `.form-label` 유틸리티 사용
- **실제 코드 감소**: 57줄

#### `user-info/+page.svelte` [✅ 완료]
- [✅] `.textarea-field` 유틸리티 사용
- [✅] CSS 변수로 색상 변환
- [✅] `.form-label` 유틸리티 사용
- **실제 코드 감소**: 36줄

#### `final-message/+page.svelte` [✅ 완료]
- [✅] `.textarea-field` 유틸리티 사용
- [✅] CSS 변수로 색상 변환
- **실제 코드 감소**: 19줄

#### `ai-settings/+page.svelte` [✅ 완료]
- [✅] `.loading-state` → app.css 유틸리티 사용
- [✅] `.form-label`, `.select-field`, `.form-hint` 유틸리티 사용
- [✅] 하드코딩 색상 (10+ 개) → CSS 변수 변환
- **실제 코드 감소**: ~50줄

#### `library/+page.svelte` [✅ 완료]
- [✅] 버튼 스타일 통일
- [✅] `.empty-state` → app.css 유틸리티 (이미 사용 중)
- [✅] `.loading-state` → app.css 유틸리티 (이미 사용 중)
- [✅] Filter 스타일 확인
- **실제 코드 감소**: 최소 (이미 양호한 상태)

---

### 🟡 Medium Priority

#### `map-settings/generator/+page.svelte` [✅ 완료]
- [✅] Form 스타일 → `.input-field`, `.textarea-field` 사용
- [✅] `.message-box` → `.alert-*` 유틸리티로 변경
- [✅] Label 스타일 → `.form-label` 사용
- [✅] 하드코딩 색상 확인 및 변환
- **실제 코드 감소**: 40-60줄

#### `map-settings/library/+page.svelte` [✅ 완료]
- [✅] 이미 `.empty-state`, `.loading-state` 사용 중 (양호)
- [✅] Filter 스타일 확인
- [✅] 하드코딩 색상 확인
- **실제 코드 감소**: 최소

#### `map-settings/rag-test/+page.svelte` [✅ 완료]
- [✅] 이미 `.empty-state`, `.loading-state` 사용 중 (양호)
- [✅] `.badge` 스타일 확인
- [✅] 하드코딩 색상 확인 (#f59e0b 등)
- **실제 코드 감소**: 최소

#### `autonomous-driving/settings/+page.svelte` [✅ 완료]
- [✅] `.alert-success`, `.alert-error` 유틸리티 사용
- [✅] 하드코딩 색상 제거 (#d1fae5, #065f46, #fee2e2, #991b1b)
- [✅] 중복 `.message` 스타일 제거
- **실제 코드 감소**: 21줄

#### `autonomous-driving/vehicle-control/+page.svelte` [✅ 완료]
- [✅] `.btn-compact` 유틸리티 사용
- [✅] `!important` 오버라이드 제거
- **실제 코드 감소**: 7줄

#### `autonomous-driving/manual-control/+page.svelte` [✅ 완료]
- [✅] 중복 `.section` 스타일 제거
- **실제 코드 감소**: 6줄

#### `autonomous-driving/triggers/+page.svelte` [✅ 완료]
- [✅] 하드코딩 색상 → CSS 변수 변환 (rgba(251, 191, 36, 0.1), rgba(72, 187, 120, 0.1), rgba(160, 174, 192, 0.1))
- [✅] 중복 `.form-group`, `.textarea-field` 스타일 제거
- [✅] 중복 `.empty-state` 스타일 제거
- **실제 코드 감소**: 34줄

#### `app-settings/+page.svelte` (renamed from `settings/+page.svelte`) [⏳ 진행 중]
- [ ] Tailwind-like 클래스명 제거 (`max-w-4xl`, `mx-auto`)
- [ ] 일관된 유틸리티 클래스 사용
- [ ] 하드코딩 색상 변환
- **예상 코드 감소**: 40줄

#### `ChatView.svelte` [⏳ 대기]
- [ ] `.empty-state` → app.css 유틸리티
- [ ] Scrollbar 스타일 중복 제거 (이미 app.css에 전역 정의됨)
- [ ] 텍스트 색상 유틸리티 클래스 사용
- **예상 코드 감소**: 20줄

---

### 🟢 Low Priority

#### `HelpModal.svelte`
- [ ] Dialog.svelte 컴포넌트로 통합
- **예상 코드 감소**: 전체 파일 제거 가능

#### `+page.svelte` (Dashboard)
- [ ] `.info-card` → `.card-interactive` 변경
- **예상 코드 감소**: 15줄

---

## 📈 예상 효과 (업데이트됨)

### 코드 감소 (현재까지)
- **AI Settings 실제 감소**: 289줄 (7개 파일)
- **Map Settings 실제 감소**: 68줄 (3개 파일)
- **Autonomous-driving Settings 실제 감소**: 68줄 (4개 파일)
- **총 코드 감소**: 425줄 (14개 파일)
- **app.css 추가**: +177줄 (재사용 가능한 유틸리티)
- **순수 코드 감소**: 248줄 (425 - 177)
- **중복 제거**: 30+ 패턴 완료
- **남은 작업**: Components (ChatView, HelpModal), Dashboard, Settings, 전체 색상 최종 점검

### 전체 예상 효과
- **총 예상 감소**: 500+ 줄
- **중복 제거**: 30+ 패턴
- **파일 정리**: 1개 제거 (HelpModal.svelte)

### 유지보수 개선
- ✅ 디자인 변경 시 app.css만 수정하면 전체 반영
- ✅ 신규 개발자 온보딩 시간 단축 (일관된 패턴)
- ✅ 버그 가능성 감소 (하드코딩 색상 제거)

### 성능 향상
- ✅ 중복 CSS 규칙 제거로 번들 크기 감소
- ✅ 브라우저 렌더링 최적화

---

## ✅ Action Items

### Immediate (이번 주)
1. [✅] app.css에 필수 유틸리티 추가
   - [✅] `.empty-state`
   - [✅] `.loading-state`
   - [✅] `.form-group`, `.form-label`, `.form-hint`, `.form-error`
   - [✅] 색상 변수 추가 (success/info/warning bg-light 변형)
   - [✅] `.textarea-field` 추가
   - [✅] `.badge`, `.badge-success`, `.badge-error`, `.badge-info`, `.badge-warning` 추가
   - [✅] `.btn-compact` 추가
   - [✅] 애니메이션 유틸리티 추가 (spin, pulse, fadeIn, slideInUp)
   - [✅] `.form-label`을 flex로 수정 (아이콘+텍스트 가로 정렬)

2. [✅] 하드코딩 색상 → CSS 변수 변환 (AI Settings 7개 파일 완료)
   - [✅] `characters/+page.svelte`
   - [✅] `commands/+page.svelte`
   - [✅] `system-messages/+page.svelte`
   - [✅] `chat-settings/+page.svelte`
   - [✅] `user-info/+page.svelte`
   - [✅] `final-message/+page.svelte`
   - [✅] `ai-settings/+page.svelte`

### Short-term (다음 주)
3. [✅] 중복 버튼 스타일 제거 (`.btn-icon` 사용) - AI Settings 완료
4. [✅] Dialog.svelte 통일 (인라인 모달 제거) - commands/+page.svelte 완료
5. [✅] Form 스타일 통일 (`.input-field`, `.select-field`, `.textarea-field` 사용) - AI Settings 완료
6. [✅] Map Settings 파일 정리 (generator, library, rag-test) - 완료
7. [✅] Autonomous-driving Settings 파일 정리 (settings, vehicle-control, manual-control, triggers) - 완료

### Long-term (2주 후)
6. [ ] 전체 파일 유틸리티 클래스 사용 검토
7. [ ] Over-abstraction 검토 및 정리
8. [ ] app.css에 JSDoc 주석 추가 (개발자 가이드)

---

## 📚 개발 가이드라인 (업데이트)

### 스타일 작성 우선순위
1. **app.css 유틸리티 클래스** 먼저 확인
2. **없으면 추가 검토** (2회 이상 사용되는 패턴인가?)
3. **컴포넌트 특화** 스타일만 `<style>` 태그에 작성

### 색상 사용 규칙
1. **유틸리티 클래스 우선**: `.text-primary`, `.bg-surface` 등
2. **필요시 CSS 변수**: `var(--color-text-primary)`
3. **하드코딩 금지**: `#1f2937` ❌

### 버튼 사용 가이드
```svelte
<!-- Primary Action -->
<button class="btn-primary">저장</button>

<!-- Secondary Action -->
<button class="btn-secondary">취소</button>

<!-- Danger Action -->
<button class="btn-danger">삭제</button>

<!-- Icon Button -->
<button class="btn-icon">
  <Icon icon="solar:pen-2-duotone" width="20" />
</button>

<!-- Icon Button (Danger) -->
<button class="btn-icon danger">
  <Icon icon="solar:trash-bin-2-duotone" width="20" />
</button>

<!-- Text Button -->
<button class="btn-text">더보기</button>
```

### Form 사용 가이드
```svelte
<div class="form-group">
  <label class="form-label" for="input-id">Label</label>
  <input type="text" id="input-id" class="input-field w-full" />
  <p class="form-hint">Hint text</p>
</div>
```

---

## 🎯 최종 목표

> **"app.css를 먼저 읽고, 있는 걸 사용하자"**

- 개발 전 app.css 전체 확인 습관화
- 중복 스타일 작성 전 유틸리티 검색
- 2회 이상 사용되는 패턴은 app.css에 추가

---

**문서 작성**: Claude Code
**마지막 업데이트**: 2025-11-23