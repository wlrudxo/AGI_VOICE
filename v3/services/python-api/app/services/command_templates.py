from app.schemas.command_templates import (
    CommandTemplate,
    CommandTemplateCreate,
    CommandTemplateUpdate,
)
from app.services.ai_chat_db import AiChatDb, get_ai_chat_db, utc_now_iso


class CommandTemplateService:
    def __init__(self, db: AiChatDb) -> None:
        self._db = db

    def list_templates(self, is_active: int | None = None) -> list[CommandTemplate]:
        sql = "SELECT * FROM command_templates"
        params: tuple[int, ...] | tuple[()] = ()
        if is_active is not None:
            sql += " WHERE is_active = ?"
            params = (is_active,)
        sql += " ORDER BY datetime(created_at) DESC"
        with self._db.with_lock(), self._db.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [CommandTemplate.model_validate(dict(row)) for row in rows]

    def create_template(self, payload: CommandTemplateCreate) -> CommandTemplate:
        now = utc_now_iso()
        with self._db.with_lock(), self._db.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO command_templates (name, content, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (payload.name, payload.content, payload.is_active, now, now),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM command_templates WHERE id = ?",
                (int(cursor.lastrowid),),
            ).fetchone()
            return CommandTemplate.model_validate(dict(row))

    def update_template(self, template_id: int, payload: CommandTemplateUpdate) -> CommandTemplate:
        now = utc_now_iso()
        with self._db.with_lock(), self._db.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE command_templates
                SET name = ?, content = ?, is_active = ?, updated_at = ?
                WHERE id = ?
                """,
                (payload.name, payload.content, payload.is_active, now, template_id),
            )
            conn.commit()
            if cursor.rowcount == 0:
                raise RuntimeError("Command template not found")
            row = conn.execute(
                "SELECT * FROM command_templates WHERE id = ?",
                (template_id,),
            ).fetchone()
            return CommandTemplate.model_validate(dict(row))

    def toggle_template(self, template_id: int) -> CommandTemplate:
        with self._db.with_lock(), self._db.connect() as conn:
            existing = conn.execute(
                "SELECT * FROM command_templates WHERE id = ?",
                (template_id,),
            ).fetchone()
            if existing is None:
                raise RuntimeError("Command template not found")
            next_active = 0 if int(existing["is_active"]) == 1 else 1
            conn.execute(
                """
                UPDATE command_templates
                SET is_active = ?, updated_at = ?
                WHERE id = ?
                """,
                (next_active, utc_now_iso(), template_id),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM command_templates WHERE id = ?",
                (template_id,),
            ).fetchone()
            return CommandTemplate.model_validate(dict(row))

    def delete_template(self, template_id: int) -> None:
        with self._db.with_lock(), self._db.connect() as conn:
            cursor = conn.execute("DELETE FROM command_templates WHERE id = ?", (template_id,))
            conn.commit()
            if cursor.rowcount == 0:
                raise RuntimeError("Command template not found")


_service = CommandTemplateService(get_ai_chat_db())


def get_command_template_service() -> CommandTemplateService:
    return _service
