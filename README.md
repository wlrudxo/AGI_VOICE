# AGI Voice V2

AI 기반 자율주행 맵 생성 및 주행 결정 연구를 위한 데스크톱 애플리케이션

## 프로젝트 개요

AGI Voice V2는 자율주행 연구를 위한 통합 플랫폼으로, 다음 기능을 제공합니다:

- **AI 채팅 시스템**: Claude AI 기반 자연어 대화 인터페이스
- **SUMO 맵 관리**: 교통 시뮬레이션 맵 생성, 편집, 라이브러리 관리
- **CarMaker 통합**: 실시간 차량 제어 및 모니터링
- **트리거 기반 자동화**: 조건 기반 자동 제어 시스템

## 기술 스택

### 프론트엔드
- **프레임워크**: Tauri 2.x + SvelteKit 2.9.0 + Svelte 5.0.0
- **스타일링**: Tailwind CSS 4.1.14
- **빌드 도구**: Vite 6.x
- **아이콘**: Iconify (Solar 듀오톤 테마)

### 백엔드
- **프레임워크**: Tauri (Rust)
- **ORM**: SeaORM
- **데이터베이스**: SQLite (ai_chat.db, sumo_maps.db)

### AI 통합
- **Claude CLI**: 자연어 처리 및 명령 실행
- **동적 프롬프트 시스템**: 캐릭터, 명령 템플릿 기반 AI 동작 제어

## 설치 및 실행

### 사전 요구사항

1. **Node.js** (v18 이상)
2. **Rust** (최신 stable 버전)
3. **Claude CLI** (선택사항 - AI 채팅 기능 사용 시 필요)
   ```bash
   # Claude CLI 설치 (npm)
   npm install -g @anthropic-ai/claude-cli

   # 또는 다른 방법으로 설치 후 PATH에 추가
   ```

4. **CarMaker** (선택사항 - 차량 제어 기능 사용 시 필요)

### 프로젝트 클론 및 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/AGI_VOICE_V2.git
cd AGI_VOICE_V2

# 의존성 설치
npm install
```

### 개발 모드 실행

```bash
# 프론트엔드만 실행 (UI 개발용)
npm run dev

# Tauri 데스크톱 앱 실행 (권장)
npm run tauri dev
```

### 프로덕션 빌드

```bash
npm run tauri build
```

빌드된 실행 파일은 `src-tauri/target/release/` 디렉토리에 생성됩니다.

## CarMaker 연동 설정

### 중요: .CarMaker.tcl 파일 설정

프로젝트에 CarMaker와의 TCP 통신을 위한 `.CarMaker.tcl` 파일이 포함되어 있습니다.

**설정 방법:**

1. 프로젝트 루트의 `.CarMaker.tcl` 파일을 **CarMaker Project 폴더**에 복사합니다
   ```
   예: C:\IPG\hil\Data\MyProject\.CarMaker.tcl
   ```

2. CarMaker를 실행하면 **자동으로 TCP 포트 16660이 열립니다**

3. AGI Voice V2 애플리케이션에서 CarMaker 연결:
   - `자율주행 > 설정` 메뉴로 이동
   - 호스트: `localhost` (또는 CarMaker가 실행 중인 IP)
   - 포트: `16660`
   - "연결" 버튼 클릭

**`.CarMaker.tcl` 파일 내용:**
```tcl
set Pgm(TcpCmdPort) 16660
```

이 설정으로 CarMaker는 시작 시 자동으로 TCP 명령 포트를 엽니다.

### CarMaker 기능 사용

1. **차량 제어** (`자율주행 > 차량 제어`)
   - 실시간 차량 상태 모니터링 (속도, 가속도, 조향각 등)
   - DVA Read를 통한 CarMaker 데이터 읽기

2. **수동 제어** (`자율주행 > 수동 제어`)
   - 조향, 가속, 브레이크 수동 입력
   - DVA Write를 통한 실시간 제어

3. **트리거** (`자율주행 > 트리거`)
   - 조건 기반 자동 제어 설정
   - 예: 속도 > 50km/h 시 자동 브레이크

## 주요 기능

### 1. AI 채팅 시스템

- **동적 프롬프트**: 시스템 메시지, 캐릭터, 명령 템플릿 조합
- **대화 기록**: SQLite 기반 영구 저장
- **위젯 모드**: 컴팩트한 채팅 전용 UI
- **자동 새로고침**: 데이터베이스 변경 감지 (2초 폴링)

**사용 방법:**
1. `AI 설정 > 채팅 설정`에서 캐릭터 및 프롬프트 선택
2. 대시보드 또는 위젯 모드에서 대화 시작
3. AI가 자동으로 명령 태그를 파싱하여 실행

### 2. SUMO 맵 관리

- **맵 생성**: XML 기반 도로망 정의 및 시각화
- **맵 라이브러리**: 저장된 맵 검색, 필터링, 편집
- **SVG 시각화**: 실시간 맵 미리보기

**사용 방법:**
1. `Map 설정 > Map 생성`에서 SUMO XML 입력
2. SVG 캔버스에서 맵 확인
3. 저장 후 라이브러리에서 관리

### 3. 데이터베이스 구조

**AI 채팅 DB** (`ai_chat.db`):
- `conversations`: 대화 세션
- `messages`: 메시지 기록
- `prompt_templates`: 시스템 메시지
- `characters`: AI 캐릭터
- `command_templates`: 명령 정의

**SUMO Maps DB** (`sumo_maps.db`):
- `maps`: 교통 맵 데이터
- `map_scenarios`: 시나리오 설정

데이터베이스는 첫 실행 시 자동 생성됩니다.

## 프로젝트 구조

```
AGI_VOICE_V2/
├── src/                      # 프론트엔드 (SvelteKit)
│   ├── routes/               # 페이지 라우트
│   │   ├── +layout.svelte    # 메인 레이아웃
│   │   ├── +page.svelte      # 대시보드
│   │   ├── ai-settings/      # AI 설정
│   │   ├── map-settings/     # 맵 관리
│   │   ├── autonomous-driving/ # CarMaker 통합
│   │   └── app-settings/     # 앱 설정
│   ├── lib/
│   │   ├── components/       # Svelte 컴포넌트
│   │   ├── stores/           # 상태 관리
│   │   ├── actions/          # AI 액션 처리
│   │   └── utils/            # 유틸리티
│   └── app.css               # 전역 스타일
├── src-tauri/                # 백엔드 (Rust)
│   ├── src/
│   │   ├── commands/         # Tauri 명령
│   │   ├── db/               # 데이터베이스
│   │   ├── ai/               # AI 통합
│   │   ├── carmaker/         # CarMaker 통합
│   │   └── triggers/         # 트리거 시스템
│   └── Cargo.toml
├── .CarMaker.tcl             # CarMaker TCP 포트 설정
├── CLAUDE.md                 # 개발 가이드 (Claude Code용)
└── package.json
```

## 개발 가이드

### 코드 컨벤션

- **Frontend**: camelCase (TypeScript/Svelte)
- **Backend**: snake_case (Rust), camelCase (Tauri 직렬화)
- **Database**: snake_case (SQLite 컬럼)

자세한 내용은 [CLAUDE.md](./CLAUDE.md)를 참조하세요.

### 주요 개발 명령어

```bash
# 개발 서버 실행
npm run dev                # Vite only (http://localhost:1420)
npm run tauri dev          # Tauri + Vite

# 코드 검사
npm run check              # Svelte + TypeScript 타입 체크
cargo check                # Rust 컴파일 체크

# 빌드
npm run tauri build        # 프로덕션 빌드
```

### 스타일링 가이드

- `src/app.css`에 정의된 유틸리티 클래스 사용 권장
- Tailwind CSS 4.x 문법 준수
- 컴포넌트 개발 전 `app.css` 확인 필수

자세한 내용은 [CLAUDE.md - Styling Guidelines](./CLAUDE.md#styling-guidelines)를 참조하세요.

## 문제 해결

### Claude CLI 없음 오류
```bash
# Claude CLI 설치 확인
claude --version

# PATH에 추가되지 않은 경우
# Windows: 시스템 환경 변수에 claude.exe 경로 추가
# macOS/Linux: ~/.bashrc 또는 ~/.zshrc에 추가
```

### CarMaker 연결 실패
1. `.CarMaker.tcl` 파일이 CarMaker Project 폴더에 있는지 확인
2. CarMaker가 실행 중인지 확인
3. 포트 16660이 방화벽에서 차단되지 않았는지 확인
4. `자율주행 > 설정`에서 연결 정보 재확인

### 데이터베이스 오류
- `ai_chat.db` 및 `sumo_maps.db` 파일이 손상된 경우:
  1. 백업이 있다면 복원
  2. 없다면 파일 삭제 후 재시작 (자동 재생성)

## 라이선스

MIT License

## 기여

이슈 및 풀 리퀘스트는 언제나 환영합니다.

## 최근 업데이트

- **SUMO Map Management System (Phase 1 완료)**
  - 맵 생성/편집/라이브러리 기능
  - SVG 시각화
  - 검색 및 필터링

- **Generic AI Chat System**
  - 동적 프롬프트 시스템
  - 위젯 모드
  - 자동 새로고침

- **CarMaker Integration**
  - 실시간 차량 제어
  - 트리거 기반 자동화
  - DVA Read/Write 지원

자세한 변경 내역은 [CLAUDE.md](./CLAUDE.md)를 참조하세요.
