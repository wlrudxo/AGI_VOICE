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
            self._reset_legacy_schema_if_needed(conn)
            self._create_tables(conn)
            conn.commit()
            self._seed_if_needed(conn)

    def _create_tables(self, conn: sqlite3.Connection) -> None:
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
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_template_id INTEGER NOT NULL,
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

    def _reset_legacy_schema_if_needed(self, conn: sqlite3.Connection) -> None:
        table_names = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        if "conversations" not in table_names and "characters" not in table_names:
            return

        needs_reset = "characters" in table_names
        if not needs_reset and "conversations" in table_names:
            conversation_columns = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(conversations)").fetchall()
            }
            needs_reset = bool({"character_id", "user_info"} & conversation_columns)

        if not needs_reset:
            return

        # Decision record:
        # solo-dev 구조 정리 단계라 캐릭터/유저정보 레거시 스키마를 유지하지 않는다.
        # 오래된 ai_chat.db가 감지되면 채팅 관련 테이블을 새 구조로 재생성한다.
        for table_name in ("messages", "conversations", "characters", "prompt_templates", "command_templates"):
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")

    def _seed_if_needed(self, conn: sqlite3.Connection) -> None:
        prompt_count = int(conn.execute("SELECT COUNT(*) FROM prompt_templates").fetchone()[0])
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
                    "기본 시스템 메시지 - 자율주행 제어",
                    "당신은 CarMaker 기반 자율주행 제어를 돕는 AI 어시스턴트입니다.\n\n"
                    "사용자의 주행 상황과 차량 상태를 바탕으로 안전하고 실행 가능한 제어 지시를 제안하세요.\n\n"
                    "주요 역할:\n"
                    "1. 속도 제어, 감속, 정지, 차선 오프셋 등 차량 제어 판단\n"
                    "2. 차량 telemetry를 바탕으로 위험 상황 분석\n"
                    "3. trigger 또는 수동 제어 상황에서 실행 가능한 명령 시퀀스 생성\n"
                    "4. 불필요한 설명보다 실제 실행 가능한 제어 명령 우선\n\n"
                    "응답 시 주의사항:\n"
                    "- 안전을 우선하고 과격한 조향/가감속을 피하세요.\n"
                    "- 가능하면 간결한 명령 시퀀스를 제시하세요.\n"
                    "- 현재 차량 상태를 반영한 판단만 하세요.",
                    now,
                    now,
                ),
            )
            conn.execute(
                """
                INSERT INTO prompt_templates (id, name, content, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    2,
                    "기본 시스템 메시지 - 맵 생성",
                    "당신은 SUMO/자율주행 시뮬레이션 맵 생성을 돕는 AI 어시스턴트입니다.\n\n"
                    "사용자의 요구사항을 바탕으로 도로 구조, 교차로, 차선, 카테고리, 난이도 등을 설계하고 맵 관련 액션을 제안하세요.\n\n"
                    "주요 역할:\n"
                    "1. 새로운 주행 시나리오용 맵 설계\n"
                    "2. 기존 맵 조회/수정/삭제 흐름 지원\n"
                    "3. 도심, 고속도로, 교차로 등 맵 유형별 특징 설명\n"
                    "4. 맵 생성 시 필요한 필드와 메타데이터 정리\n\n"
                    "응답 시 주의사항:\n"
                    "- 맵 구조와 용도를 분명히 설명하세요.\n"
                    "- 필요한 경우 맵 액션 태그를 사용하세요.\n"
                    "- 사용자의 의도를 반영해 카테고리와 난이도를 제안하세요.",
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

        self._ensure_default_prompt_templates(conn)
        self._ensure_default_command_templates(conn)
        self._remove_legacy_command_templates(conn)

        conn.commit()

    def _ensure_default_prompt_templates(self, conn: sqlite3.Connection) -> None:
        now = utc_now_iso()
        defaults = [
            (
                "기본 시스템 메시지 - 자율주행 제어",
                "당신은 CarMaker 기반 자율주행 제어를 돕는 AI 어시스턴트입니다.\n\n"
                "사용자의 주행 상황과 차량 상태를 바탕으로 안전하고 실행 가능한 제어 지시를 제안하세요.\n\n"
                "주요 역할:\n"
                "1. 속도 제어, 감속, 정지, 차선 오프셋 등 차량 제어 판단\n"
                "2. 차량 telemetry를 바탕으로 위험 상황 분석\n"
                "3. trigger 또는 수동 제어 상황에서 실행 가능한 명령 시퀀스 생성\n"
                "4. 불필요한 설명보다 실제 실행 가능한 제어 명령 우선\n\n"
                "응답 시 주의사항:\n"
                "- 안전을 우선하고 과격한 조향/가감속을 피하세요.\n"
                "- 가능하면 간결한 명령 시퀀스를 제시하세요.\n"
                "- 현재 차량 상태를 반영한 판단만 하세요.",
            ),
            (
                "기본 시스템 메시지 - 맵 생성",
                "당신은 SUMO/자율주행 시뮬레이션 맵 생성을 돕는 AI 어시스턴트입니다.\n\n"
                "사용자의 요구사항을 바탕으로 도로 구조, 교차로, 차선, 카테고리, 난이도 등을 설계하고 맵 관련 액션을 제안하세요.\n\n"
                "주요 역할:\n"
                "1. 새로운 주행 시나리오용 맵 설계\n"
                "2. 기존 맵 조회/수정/삭제 흐름 지원\n"
                "3. 도심, 고속도로, 교차로 등 맵 유형별 특징 설명\n"
                "4. 맵 생성 시 필요한 필드와 메타데이터 정리\n\n"
                "응답 시 주의사항:\n"
                "- 맵 구조와 용도를 분명히 설명하세요.\n"
                "- 필요한 경우 맵 액션 태그를 사용하세요.\n"
                "- 사용자의 의도를 반영해 카테고리와 난이도를 제안하세요.",
            ),
        ]

        for name, content in defaults:
            existing = conn.execute(
                "SELECT id FROM prompt_templates WHERE name = ?",
                (name,),
            ).fetchone()
            if existing is not None:
                continue

            conn.execute(
                """
                INSERT INTO prompt_templates (name, content, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (name, content, now, now),
            )

    def _ensure_default_command_templates(self, conn: sqlite3.Connection) -> None:
        now = utc_now_iso()
        defaults = [
            (
                "자율주행 맵 관리",
                "## 자율주행 맵 관리 명령어\n\n"
                "사용자가 맵 생성, 조회, 수정, 삭제를 요청하면 맵 관련 액션 태그를 사용하세요.\n"
                "<read_map>\n"
                "<map|name:맵이름|description:설명|category:카테고리|difficulty:난이도>\n"
                "<update_map|id:맵ID|수정할필드:새값>\n"
                "<delete_map|id:맵ID>",
                1,
            ),
            (
                "자율주행 제어",
                "## 자율주행 제어 명령어\n\n"
                "차량 제어가 필요할 때는 아래 형식의 제어 명령만 출력하세요.\n"
                "설명 문장 대신 명령 블록을 우선 사용합니다.\n\n"
                "### 기본 형식\n"
                "```text\n"
                "DM.Gas = 0.3 | 2000 | Abs\n"
                "DM.Brake = 0.0 | 2000 | Abs\n"
                "DM.Steer.Ang = 0.1 | 1500 | Abs\n"
                "DM.v.Trgt = 15 | 3000 | Abs\n"
                "DM.LaneOffset = 0.5 | 3000 | Abs\n"
                "```\n\n"
                "### 대기 명령\n"
                "```text\n"
                "wait(1000)\n"
                "wait_until Car.v < 0.5 5000\n"
                "```\n\n"
                "### 규칙\n"
                "- 값 형식: 변수 = 값 | duration(ms) | mode\n"
                "- mode는 Abs, AbsRamp, FacRamp 중 하나를 사용합니다.\n"
                "- duration이 -1이면 무기한 유지입니다.\n"
                "- 필요할 때만 최소한의 명령을 출력합니다.\n"
                "- 자연어 설명보다 실행 가능한 명령 시퀀스를 우선합니다.\n\n"
                "### 자주 쓰는 변수\n"
                "- DM.Gas: 가속 페달 (0~1)\n"
                "- DM.Brake: 브레이크 페달 (0~1)\n"
                "- DM.Steer.Ang: 조향 각도\n"
                "- DM.v.Trgt: 목표 속도\n"
                "- DM.LaneOffset: 차선 중심 대비 오프셋\n"
                "- SC.TAccel: 시뮬레이션 시간 배율",
                1,
            ),
        ]

        for name, content, is_active in defaults:
            existing = conn.execute(
                "SELECT id FROM command_templates WHERE name = ?",
                (name,),
            ).fetchone()
            if existing is not None:
                continue

            conn.execute(
                """
                INSERT INTO command_templates (name, content, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, content, is_active, now, now),
            )

    def _remove_legacy_command_templates(self, conn: sqlite3.Connection) -> None:
        # Decision record:
        # "예제 명령어 템플릿"은 실제 제품 동작에 기여하지 않고 사용자 선택만 흐린다.
        # 기본 제공 목록에서 제거하고, 기존 DB에 남아 있던 레거시 항목도 자동 정리한다.
        conn.execute(
            "DELETE FROM command_templates WHERE name = ?",
            ("예제 명령어 템플릿",),
        )


_settings = get_settings()
_service = AiChatDb(_settings.data_dir_path / "ai_chat.db")


def get_ai_chat_db() -> AiChatDb:
    return _service
