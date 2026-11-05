import base64
import binascii
from typing import Literal

from pydantic import BaseModel, ConfigDict, TypeAdapter, ValidationError, field_validator


CHAT_PATH = "/ai-assistant/chat"
CONVERSATION_HEADER = b"x-ai-conversation"
NO_STORE = {"Cache-Control": "no-store"}
MAX_CONVERSATION_BYTES = 7500
MAX_MESSAGES = 40
MAX_USER_MESSAGE_LENGTH = 2000


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant"]
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("消息不能为空")
        return value


_messages_adapter = TypeAdapter(list[ChatMessage])


def parse_conversation(encoded: bytes) -> list[ChatMessage]:
    if len(encoded) > MAX_CONVERSATION_BYTES:
        raise ValueError("对话已达到长度上限，请开启新对话。")
    try:
        padded = encoded + b"=" * (-len(encoded) % 4)
        messages = _messages_adapter.validate_json(base64.b64decode(padded, altchars=b"-_", validate=True))
    except (ValidationError, binascii.Error):
        raise ValueError("对话消息格式错误。") from None

    if not messages or messages[-1].role != "user":
        raise ValueError("请先输入要发送的消息。")
    if len(messages) > MAX_MESSAGES:
        raise ValueError("对话已达到消息数量上限，请开启新对话。")
    for index, message in enumerate(messages):
        if message.role != ("user" if index % 2 == 0 else "assistant"):
            raise ValueError("对话消息顺序错误。")
        if message.role == "user" and len(message.content) > MAX_USER_MESSAGE_LENGTH:
            raise ValueError(f"单条提问最多 {MAX_USER_MESSAGE_LENGTH} 个字符。")
    return messages
