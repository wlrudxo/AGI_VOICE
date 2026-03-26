from app.schemas.ai_catalog import (
    Character,
    CharacterCreate,
    CharacterUpdate,
    PromptTemplate,
    PromptTemplateCreate,
    PromptTemplateUpdate,
)
from app.services.ai_chat_db import AiChatDb, get_ai_chat_db, utc_now_iso


class AiCatalogService:
    def __init__(self, db: AiChatDb) -> None:
        self._db = db

    def list_characters(self) -> list[Character]:
        with self._db.with_lock(), self._db.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM characters ORDER BY id ASC"
            ).fetchall()
            return [Character.model_validate(dict(row)) for row in rows]

    def list_prompt_templates(self) -> list[PromptTemplate]:
        with self._db.with_lock(), self._db.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM prompt_templates ORDER BY id ASC"
            ).fetchall()
            return [PromptTemplate.model_validate(dict(row)) for row in rows]

    def create_character(self, payload: CharacterCreate) -> Character:
        now = utc_now_iso()
        with self._db.with_lock(), self._db.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO characters (name, prompt_content, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (payload.name, payload.prompt_content, now, now),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM characters WHERE id = ?",
                (int(cursor.lastrowid),),
            ).fetchone()
            return Character.model_validate(dict(row))

    def update_character(self, character_id: int, payload: CharacterUpdate) -> Character:
        now = utc_now_iso()
        with self._db.with_lock(), self._db.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE characters
                SET name = ?, prompt_content = ?, updated_at = ?
                WHERE id = ?
                """,
                (payload.name, payload.prompt_content, now, character_id),
            )
            conn.commit()
            if cursor.rowcount == 0:
                raise RuntimeError("Character not found")
            row = conn.execute(
                "SELECT * FROM characters WHERE id = ?",
                (character_id,),
            ).fetchone()
            return Character.model_validate(dict(row))

    def delete_character(self, character_id: int) -> None:
        with self._db.with_lock(), self._db.connect() as conn:
            cursor = conn.execute("DELETE FROM characters WHERE id = ?", (character_id,))
            conn.commit()
            if cursor.rowcount == 0:
                raise RuntimeError("Character not found")

    def create_prompt_template(self, payload: PromptTemplateCreate) -> PromptTemplate:
        now = utc_now_iso()
        with self._db.with_lock(), self._db.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO prompt_templates (name, content, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (payload.name, payload.content, now, now),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM prompt_templates WHERE id = ?",
                (int(cursor.lastrowid),),
            ).fetchone()
            return PromptTemplate.model_validate(dict(row))

    def update_prompt_template(
        self,
        template_id: int,
        payload: PromptTemplateUpdate,
    ) -> PromptTemplate:
        now = utc_now_iso()
        with self._db.with_lock(), self._db.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE prompt_templates
                SET name = ?, content = ?, updated_at = ?
                WHERE id = ?
                """,
                (payload.name, payload.content, now, template_id),
            )
            conn.commit()
            if cursor.rowcount == 0:
                raise RuntimeError("Prompt template not found")
            row = conn.execute(
                "SELECT * FROM prompt_templates WHERE id = ?",
                (template_id,),
            )
            return PromptTemplate.model_validate(dict(row.fetchone()))

    def delete_prompt_template(self, template_id: int) -> None:
        with self._db.with_lock(), self._db.connect() as conn:
            cursor = conn.execute("DELETE FROM prompt_templates WHERE id = ?", (template_id,))
            conn.commit()
            if cursor.rowcount == 0:
                raise RuntimeError("Prompt template not found")


_service = AiCatalogService(get_ai_chat_db())


def get_ai_catalog_service() -> AiCatalogService:
    return _service
