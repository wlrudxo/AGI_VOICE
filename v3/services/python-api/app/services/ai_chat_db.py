import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import get_settings


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AiChatDb:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._lock = threading.RLock()
        self._init_db()

    @property
    def db_path(self) -> Path:
        return self._db_path

    def connect(self) -> sqlite3.Connection:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def with_lock(self):
        return self._lock

    def _init_db(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock, self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS prompt_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    prompt_content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER NOT NULL,
                    prompt_template_id INTEGER NOT NULL,
                    user_info TEXT,
                    title TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS command_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()
            self._seed_if_needed(conn)

    def _seed_if_needed(self, conn: sqlite3.Connection) -> None:
        prompt_count = int(conn.execute("SELECT COUNT(*) FROM prompt_templates").fetchone()[0])
        character_count = int(conn.execute("SELECT COUNT(*) FROM characters").fetchone()[0])
        command_count = int(conn.execute("SELECT COUNT(*) FROM command_templates").fetchone()[0])

        if prompt_count == 0:
            now = utc_now_iso()
            conn.execute(
                """
                INSERT INTO prompt_templates (id, name, content, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    1,
                    "기본 시스템 메시지",
                    "당신은 자율주행 연구를 돕는 AI 어시스턴트입니다.\n\n"
                    "사용자의 자율주행 관련 질문에 답변하고, 맵 생성 및 주행 판단에 대한 연구를 지원합니다.\n\n"
                    "주요 역할:\n"
                    "1. 자율주행 기술에 대한 설명과 조언\n"
                    "2. 맵 생성 알고리즘에 대한 논의\n"
                    "3. 주행 판단 로직 분석 및 개선 제안\n"
                    "4. 연구 데이터 분석 및 인사이트 제공\n"
                    "5. 관련 문헌 및 최신 기술 동향 설명\n\n"
                    "응답 시 주의사항:\n"
                    "- 전문적이면서도 이해하기 쉽게 설명하세요.\n"
                    "- 필요시 수식이나 알고리즘을 제시하세요.\n"
                    "- 안전성과 윤리적 측면을 고려하세요.",
                    now,
                    now,
                ),
            )

        if character_count == 0:
            now = utc_now_iso()
            conn.execute(
                """
                INSERT INTO characters (id, name, prompt_content, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    1,
                    "Research Assistant",
                    "# Character: Professional Research Assistant\n\n"
                    "## 기본 설정\n"
                    "- 역할: 자율주행 연구 어시스턴트\n"
                    "- 성격: 전문적, 논리적, 친절함\n"
                    "- 특징: 명확한 설명, 근거 기반 답변, 최신 연구 동향 파악\n\n"
                    "## 말투 특징\n"
                    "- 존댓말 사용 (~입니다, ~해요)\n"
                    "- 전문 용어를 적절히 사용하되 쉽게 풀어 설명\n"
                    "- 논리적이고 체계적인 답변 구조\n\n"
                    "## 역할\n"
                    "자율주행 연구를 전문적으로 지원하는 AI 어시스턴트입니다.\n"
                    "명확한 설명과 근거 기반 조언을 제공합니다.",
                    now,
                    now,
                ),
            )

        if command_count == 0:
            now = utc_now_iso()
            conn.execute(
                """
                INSERT INTO command_templates (id, name, content, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    1,
                    "자율주행 맵 관리",
                    "## 자율주행 맵 관리 명령어\n\n"
                    "사용자가 맵 생성, 조회, 수정, 삭제를 요청하면 맵 관련 액션 태그를 사용하세요.\n"
                    "<read_map>\n<map|name:맵이름|description:설명|category:카테고리|difficulty:난이도>\n"
                    "<update_map|id:맵ID|수정할필드:새값>\n<delete_map|id:맵ID>",
                    1,
                    now,
                    now,
                ),
            )
            conn.execute(
                """
                INSERT INTO command_templates (id, name, content, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    2,
                    "예제 명령어 템플릿",
                    "## 예제 명령어 템플릿\n\n<action_type|field:value|field:value|...>",
                    0,
                    now,
                    now,
                ),
            )

        conn.commit()


_settings = get_settings()
_service = AiChatDb(_settings.data_dir_path / "ai_chat.db")


def get_ai_chat_db() -> AiChatDb:
    return _service
