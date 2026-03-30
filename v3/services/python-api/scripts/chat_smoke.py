import argparse
import asyncio
import sys

from app.schemas.chat import ChatRequest
from app.services.ai_catalog import get_ai_catalog_service
from app.services.chat import get_chat_service
from app.services.settings import get_settings_service


def resolve_defaults() -> tuple[int, int, str]:
    settings = get_settings_service().get_chat_settings()
    catalog = get_ai_catalog_service()

    character_id = settings.default_character_id
    prompt_template_id = settings.default_prompt_template_id
    model = settings.default_claude_model or "sonnet"

    if character_id is None:
        characters = catalog.list_characters()
        character_id = characters[0].id if characters else None

    if prompt_template_id is None:
        templates = catalog.list_prompt_templates()
        prompt_template_id = templates[0].id if templates else None

    if character_id is None or prompt_template_id is None:
        raise RuntimeError("Missing default character/prompt template")

    return character_id, prompt_template_id, model


async def run_smoke(real: bool, message: str) -> int:
    service = get_chat_service()
    character_id, prompt_template_id, model = resolve_defaults()

    if not real:
        async def fake_run_claude(prompt: str, model_name: str, workspace_dir):
            return f"[mock:{model_name}] {message}"

        service._run_claude = fake_run_claude  # type: ignore[attr-defined]

    request = ChatRequest(
        message=message,
        model=model,
        role="user",
        character_id=character_id,
        prompt_template_id=prompt_template_id,
        user_name="Smoke Test",
        user_info="backend smoke test",
        final_message="간단히 응답하세요.",
        no_save=True,
    )

    print("== Chat Smoke ==")
    print(f"mode={'real' if real else 'mock'}")
    print(f"character_id={character_id}")
    print(f"prompt_template_id={prompt_template_id}")
    print(f"model={model}")

    try:
        response = await service.chat(request)
    except Exception as exc:
        print("RESULT=FAIL")
        print(f"ERROR={type(exc).__name__}: {exc}")
        return 1

    print("RESULT=OK")
    print(f"conversation_id={response.conversation_id}")
    print(f"response={response.responses[0] if response.responses else ''}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test V3 chat backend")
    parser.add_argument("--real", action="store_true", help="Run the real Claude CLI path")
    parser.add_argument(
        "--message",
        default="안녕하세요. 채팅 스모크 테스트입니다.",
        help="Message to send",
    )
    args = parser.parse_args()
    return asyncio.run(run_smoke(real=args.real, message=args.message))


if __name__ == "__main__":
    raise SystemExit(main())
