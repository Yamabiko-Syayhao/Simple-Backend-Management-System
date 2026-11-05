import json
from collections.abc import AsyncIterator
from contextlib import aclosing

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from loguru import logger
from starlette.background import BackgroundTask

from app.api.v1.system.user.model import User
from app.shared.constants.codes import CodeEnum
from app.shared.exceptions import AccessTokenFail
from app.utils.current_user import current_user
from app.utils.response import HttpResponse

from .schema import CHAT_PATH, NO_STORE, ChatMessage, parse_conversation
from .service import AssistantError, stream_assistant


# 使用普通路由，避免对话回复进入后台操作日志。
AiAssistantRouter = APIRouter(tags=["AI 助手"])
REQUEST_ERROR = "AI 助手暂时无法回复，请稍后重试。"


def _encode_event(event: dict) -> bytes:
    return (json.dumps(event, ensure_ascii=False) + "\n").encode("utf-8")


async def _stream_events(user: User, messages: list[ChatMessage]) -> AsyncIterator[bytes]:
    yield _encode_event({"type": "status", "text": "正在连接模型…"})
    try:
        async with aclosing(stream_assistant(user, messages)) as events:
            async for event in events:
                yield _encode_event(event)
    except AssistantError as exc:
        yield _encode_event({"type": "error", "message": str(exc)})
    except Exception as exc:
        logger.error("AI 助手流式回复失败 ({})", type(exc).__name__)
        yield _encode_event({"type": "error", "message": REQUEST_ERROR})
    else:
        yield _encode_event({"type": "done"})


@AiAssistantRouter.get(CHAT_PATH, summary="AI 助手流式对话", response_class=StreamingResponse)
async def chat(request: Request):
    try:
        session = await current_user()
        if not session.get("id") or session.get("member_id") or session.get("user_type") == "member":
            raise AccessTokenFail()
        user = await User.get(session["id"])
        if user is None or user.status != 1:
            raise AccessTokenFail()
    except AccessTokenFail as exc:
        return await HttpResponse.success(code=exc.code, msg=exc.msg, headers=NO_STORE)
    except Exception as exc:
        logger.error("AI 助手请求失败 ({})", type(exc).__name__)
        return await HttpResponse.success(code=CodeEnum.PARTNER_CODE_FAIL.code, msg=REQUEST_ERROR, headers=NO_STORE)

    try:
        messages = parse_conversation(getattr(request.state, "ai_conversation", b""))
    except ValueError as exc:
        return await HttpResponse.success(code=CodeEnum.PARTNER_CODE_FAIL.code, msg=str(exc), headers=NO_STORE)

    events = _stream_events(user, messages)
    return StreamingResponse(
        events,
        media_type="application/x-ndjson",
        headers={**NO_STORE, "X-Accel-Buffering": "no"},
        background=BackgroundTask(events.aclose),
    )
