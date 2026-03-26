import json
import math
import os
import sqlite3
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import get_settings
from app.schemas.maps import (
    BuildResult,
    CreateMapRequest,
    EmbedResult,
    GetMapsQuery,
    MapRecord,
    MapSearchResult,
    UpdateMapRequest,
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MapService:
    EMBEDDING_MODEL = "text-embedding-3-small"

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._lock = threading.RLock()
        self._init_db()

    def create_map(self, request: CreateMapRequest) -> MapRecord:
        now = utc_now_iso()
        with self._lock, self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO maps (
                    name, description, node_xml, edge_xml, tags, category, difficulty, metadata,
                    is_embedded, embedded_at, embedding_model, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, NULL, NULL, ?, ?)
                """,
                (
                    request.name,
                    request.description,
                    request.node_xml,
                    request.edge_xml,
                    self._to_json_string(request.tags),
                    request.category or "general",
                    request.difficulty or "medium",
                    self._to_json_string(request.metadata),
                    now,
                    now,
                ),
            )
            map_id = int(cursor.lastrowid)
            conn.commit()
            return self.get_map_by_id(map_id)

    def get_maps(self, query: GetMapsQuery | None = None) -> list[MapRecord]:
        sql = "SELECT * FROM maps"
        conditions: list[str] = []
        params: list[object] = []

        if query:
            if query.category:
                conditions.append("category = ?")
                params.append(query.category)
            if query.is_embedded is not None:
                conditions.append("is_embedded = ?")
                params.append(1 if query.is_embedded else 0)
            if query.search:
                conditions.append("(name LIKE ? OR description LIKE ?)")
                like = f"%{query.search}%"
                params.extend([like, like])

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY datetime(created_at) DESC"

        with self._lock, self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [self._row_to_map(row) for row in rows]

    def get_map_by_id(self, map_id: int) -> MapRecord:
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT * FROM maps WHERE id = ?", (map_id,)).fetchone()
            if row is None:
                raise RuntimeError(f"Map not found: {map_id}")
            return self._row_to_map(row)

    def update_map(self, map_id: int, request: UpdateMapRequest) -> MapRecord:
        existing = self.get_map_by_id(map_id)
        payload = request.model_dump(exclude_unset=True, by_alias=False)
        next_values = {
            "name": payload.get("name", existing.name),
            "description": payload.get("description", existing.description),
            "node_xml": payload.get("node_xml", existing.node_xml),
            "edge_xml": payload.get("edge_xml", existing.edge_xml),
            # V2 treats explicit null the same as "field omitted" for optional updates.
            "tags": (
                self._to_json_string(payload["tags"])
                if "tags" in payload and payload["tags"] is not None
                else existing.tags
            ),
            "category": payload.get("category") or existing.category,
            "difficulty": payload.get("difficulty") or existing.difficulty,
            "metadata": (
                self._to_json_string(payload["metadata"])
                if "metadata" in payload and payload["metadata"] is not None
                else existing.metadata
            ),
            "updated_at": utc_now_iso(),
        }

        with self._lock, self._connect() as conn:
            conn.execute(
                """
                UPDATE maps
                SET name = ?, description = ?, node_xml = ?, edge_xml = ?, tags = ?, category = ?,
                    difficulty = ?, metadata = ?, is_embedded = 0, embedded_at = NULL,
                    embedding_model = NULL, updated_at = ?
                WHERE id = ?
                """,
                (
                    next_values["name"],
                    next_values["description"],
                    next_values["node_xml"],
                    next_values["edge_xml"],
                    next_values["tags"],
                    next_values["category"],
                    next_values["difficulty"],
                    next_values["metadata"],
                    next_values["updated_at"],
                    map_id,
                ),
            )
            conn.execute("DELETE FROM map_search_index WHERE map_id = ?", (map_id,))
            conn.commit()
        return self.get_map_by_id(map_id)

    def delete_map(self, map_id: int) -> None:
        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM map_search_index WHERE map_id = ?", (map_id,))
            conn.execute("DELETE FROM maps WHERE id = ?", (map_id,))
            conn.commit()

    def get_map_count(self) -> int:
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS count FROM maps").fetchone()
            return int(row["count"])

    def embed_map(self, map_id: int) -> EmbedResult:
        self.get_map_by_id(map_id)
        payload = self._run_mapgenerator_json(
            "embed_map.py",
            [str(map_id), str(self._resolve_embedding_index_path()), str(self._db_path)],
        )
        return EmbedResult.model_validate(payload)

    def build_all_embeddings(self, rebuild: bool = False) -> BuildResult:
        args = [str(self._resolve_embedding_index_path()), str(self._db_path)]
        if rebuild:
            args.append("--rebuild")
        payload = self._run_mapgenerator_json("build_all_embeddings.py", args)
        return BuildResult.model_validate(payload)

    def embeddings_health(self) -> str:
        return (
            "Embeddings module OK\n"
            f"Index path: {self._resolve_embedding_index_path()}\n"
            f"DB path: {self._db_path}"
        )

    def search_maps(self, query: str, top_k: int = 5) -> list[MapSearchResult]:
        normalized_query = query.strip()
        if not normalized_query:
            return []
        if not self._embedding_index_is_ready():
            raise RuntimeError(
                f"FAISS index not found at {self._resolve_embedding_index_path()}. "
                "Please build embeddings first."
            )

        payload = self._run_mapgenerator_json(
            "search_maps.py",
            [normalized_query, str(self._resolve_embedding_index_path()), str(self._db_path), str(top_k)],
        )
        if not isinstance(payload, list):
            raise RuntimeError("Invalid search response from MapGenerator")
        return [MapSearchResult.model_validate(item) for item in payload]

    def _search_result_from_map(
        self, map_record: MapRecord, similarity_score: float, distance: float
    ) -> MapSearchResult:
        tags: list[str] = []
        if map_record.tags:
            try:
                parsed = json.loads(map_record.tags)
                if isinstance(parsed, list):
                    tags = [str(item) for item in parsed]
            except json.JSONDecodeError:
                tags = []

        return MapSearchResult(
            map_id=map_record.id,
            map_name=map_record.name,
            description=map_record.description,
            category=map_record.category,
            difficulty=map_record.difficulty,
            tags=tags,
            similarity_score=similarity_score,
            distance=distance,
            is_embedded=map_record.is_embedded == 1,
        )

    def _build_search_text(self, map_record: MapRecord) -> str:
        parts = [map_record.name, map_record.description, map_record.category, map_record.difficulty]
        if map_record.tags:
            parts.append(map_record.tags)
        parts.append(self._extract_xml_summary(map_record.node_xml))
        parts.append(self._extract_xml_summary(map_record.edge_xml))
        return "\n".join(part for part in parts if part).strip()

    def _extract_xml_summary(self, xml_text: str) -> str:
        condensed = " ".join(xml_text.replace("<", " <").replace(">", "> ").split())
        return condensed[:4000]

    def _to_json_string(self, value) -> str | None:
        if value is None:
            return None
        return json.dumps(value, ensure_ascii=False)

    def _row_to_map(self, row: sqlite3.Row) -> MapRecord:
        return MapRecord.model_validate(dict(row))

    def _connect(self) -> sqlite3.Connection:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _fts_available(self, conn: sqlite3.Connection) -> bool:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='map_search_index'"
        ).fetchone()
        return row is not None

    def _fts_query(self, raw_query: str) -> str:
        tokens = [token for token in raw_query.replace('"', " ").split() if token]
        if not tokens:
            return raw_query
        return " OR ".join(tokens)

    def _init_db(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            self._migrate_legacy_schema(conn)
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS maps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    node_xml TEXT NOT NULL,
                    edge_xml TEXT NOT NULL,
                    tags TEXT,
                    category TEXT NOT NULL DEFAULT 'general',
                    difficulty TEXT NOT NULL DEFAULT 'medium',
                    metadata TEXT,
                    is_embedded INTEGER NOT NULL DEFAULT 0,
                    embedded_at TEXT,
                    embedding_model TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS map_scenarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    map_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    drivers TEXT,
                    vehicles TEXT,
                    traffic_config TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (map_id) REFERENCES maps (id) ON DELETE CASCADE
                )
                """
            )
            try:
                conn.execute(
                    """
                    CREATE VIRTUAL TABLE IF NOT EXISTS map_search_index
                    USING fts5(map_id UNINDEXED, content)
                    """
                )
            except sqlite3.OperationalError:
                pass
            conn.commit()

    def _resolve_embedding_index_path(self) -> Path:
        # V2 parity: embeddings/search scripts store a FAISS index under the app data directory.
        index_path = get_settings().data_dir_path / "faiss_index"
        index_path.mkdir(parents=True, exist_ok=True)
        return index_path

    def _embedding_index_is_ready(self) -> bool:
        return (self._resolve_embedding_index_path() / "index.faiss").exists()

    def _migrate_legacy_schema(self, conn: sqlite3.Connection) -> None:
        create_sql_row = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='maps'"
        ).fetchone()
        if create_sql_row is None:
            return

        create_sql = str(create_sql_row["sql"] or "").upper()
        if "NAME TEXT NOT NULL UNIQUE" not in create_sql:
            return

        conn.execute("ALTER TABLE maps RENAME TO maps_legacy_unique")
        conn.execute(
            """
            CREATE TABLE maps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                node_xml TEXT NOT NULL,
                edge_xml TEXT NOT NULL,
                tags TEXT,
                category TEXT NOT NULL DEFAULT 'general',
                difficulty TEXT NOT NULL DEFAULT 'medium',
                metadata TEXT,
                is_embedded INTEGER NOT NULL DEFAULT 0,
                embedded_at TEXT,
                embedding_model TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            INSERT INTO maps (
                id, name, description, node_xml, edge_xml, tags, category, difficulty, metadata,
                is_embedded, embedded_at, embedding_model, created_at, updated_at
            )
            SELECT
                id, name, description, node_xml, edge_xml, tags, category, difficulty, metadata,
                is_embedded, embedded_at, embedding_model, created_at, updated_at
            FROM maps_legacy_unique
            """
        )
        conn.execute("DROP TABLE maps_legacy_unique")

    def _resolve_mapgenerator_script(self, script_name: str) -> Path:
        candidates = [
            Path(__file__).resolve().parents[5] / "MapGenerator" / script_name,
            Path.cwd() / "MapGenerator" / script_name,
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        raise RuntimeError(
            "MapGenerator script not found: "
            + ", ".join(str(candidate) for candidate in candidates)
        )

    def _python_command(self) -> list[str]:
        if os.name == "nt":
            return [sys.executable]
        return [sys.executable]

    def _run_mapgenerator_json(self, script_name: str, args: list[str]) -> dict | list:
        script_path = self._resolve_mapgenerator_script(script_name)
        completed = subprocess.run(
            [*self._python_command(), str(script_path), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(script_path.parent),
        )

        if completed.returncode != 0:
            stderr = (completed.stderr or "").strip()
            if "OPENAI_API_KEY" in stderr or "api_key" in stderr:
                raise RuntimeError(
                    "OPENAI_API_KEY is required for map embeddings/search. "
                    "Please configure it before using RAG features."
                )
            raise RuntimeError(stderr or completed.stdout.strip() or "MapGenerator script failed")

        stdout = (completed.stdout or "").strip()
        if not stdout:
            raise RuntimeError("MapGenerator returned empty response")
        return json.loads(stdout)


_settings = get_settings()
_service = MapService(_settings.data_dir_path / "sumo_maps.db")


def get_map_service() -> MapService:
    return _service
