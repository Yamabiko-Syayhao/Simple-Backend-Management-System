import asyncio
import base64
import json
from contextlib import suppress
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI

from app.api.v1.system.ai_assistant import controller
from app.api.v1.system.ai_assistant.schema import CHAT_PATH, CONVERSATION_HEADER
from app.config.setting import settings
from app.scripts import init_app


@pytest.mark.parametrize("end", ["done", "error", "disconnect"])
async def test_ai_reply_streams_before_completion_and_closes(monkeypatch, end):
    release = asyncio.Event()
    closed = asyncio.Event()

    async def model_stream(user, messages):
        assert messages[0].content == "商品有多少？"
        try:
            yield {"type": "delta", "text": "共有"}
            await release.wait()
            if end == "error":
                raise controller.AssistantError("模型连接中断。")
            yield {"type": "delta", "text": "两件商品。"}
        finally:
            closed.set()

    monkeypatch.setattr(init_app, "_login_verification", AsyncMock())
    monkeypatch.setattr(controller, "current_user", AsyncMock(return_value={"id": 1}))
    monkeypatch.setattr(controller.User, "get", AsyncMock(return_value=SimpleNamespace(status=1)))
    monkeypatch.setattr(controller, "stream_assistant", model_stream)
    app = FastAPI()
    init_app.register_middlewares(app)
    app.include_router(controller.AiAssistantRouter, prefix=settings.API_PREFIX)

    conversation = json.dumps([{"role": "user", "content": "商品有多少？"}]).encode("utf-8")
    path = settings.API_PREFIX + CHAT_PATH
    scope = {
        "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "scheme": "http",
        "method": "GET", "path": path, "raw_path": path.encode(), "query_string": b"",
        "root_path": "", "headers": [(CONVERSATION_HEADER, base64.urlsafe_b64encode(conversation).rstrip(b"="))],
    }
    incoming, outgoing = asyncio.Queue(), asyncio.Queue()
    await incoming.put({"type": "http.request", "body": b"", "more_body": False})
    request = asyncio.create_task(app(scope, incoming.get, outgoing.put))

    try:
        start = await asyncio.wait_for(outgoing.get(), timeout=2)
        assert start["status"] == 200
        headers = dict(start["headers"])
        assert headers[b"content-type"] == b"application/x-ndjson"
        assert headers[b"cache-control"] == b"no-store"
        assert headers[b"x-accel-buffering"] == b"no"

        status = await asyncio.wait_for(outgoing.get(), timeout=2)
        assert json.loads(status["body"])["type"] == "status"
        delta = await asyncio.wait_for(outgoing.get(), timeout=2)
        assert delta["more_body"] and json.loads(delta["body"]) == {"type": "delta", "text": "共有"}
        assert not closed.is_set()

        if end == "disconnect":
            await incoming.put({"type": "http.disconnect"})
        else:
            release.set()
        await asyncio.wait_for(request, timeout=2)
        assert closed.is_set()

        tail = []
        while not outgoing.empty():
            body = outgoing.get_nowait().get("body")
            if body:
                tail.append(json.loads(body))
        if end == "done":
            assert tail == [{"type": "delta", "text": "两件商品。"}, {"type": "done"}]
        elif end == "error":
            assert tail == [{"type": "error", "message": "模型连接中断。"}]
        else:
            assert not tail
    finally:
        request.cancel()
        with suppress(asyncio.CancelledError):
            await request
