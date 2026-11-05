from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.api.v1.system.user import controller, service
from app.api.v1.system.user.model import User, UserRole
from app.api.v1.system.user.schema import UserIn
from app.core import dependencies
from app.core.permission import PermissionService
from app.shared.exceptions import PermissionNotEnough


@pytest.mark.parametrize(
    "field, value",
    [("user_type", 10), ("status", 1), ("dept_id", 2), ("roles", [1]), ("password", "new-password")],
)
async def test_profile_update_requires_edit_permission_for_managed_fields(monkeypatch, field, value):
    session = AsyncMock(return_value={"id": 42})
    monkeypatch.setattr(controller, "current_user", session)
    monkeypatch.setattr(dependencies, "current_user", session)
    monkeypatch.setattr(User, "get", AsyncMock(return_value=SimpleNamespace(user_type=20)))
    monkeypatch.setattr(PermissionService, "get_permission_codes", AsyncMock(return_value=["user:add"]))
    save = AsyncMock()
    monkeypatch.setattr(service.UserService, "save_or_update", save)

    params = UserIn(id=42, username="test-user", nickname="测试账号", **{field: value})
    with pytest.raises(PermissionNotEnough):
        await controller.save_or_update(params)
    save.assert_not_awaited()


async def test_profile_update_leaves_roles_and_managed_fields_unchanged(monkeypatch):
    session = AsyncMock(return_value={"id": 42})
    monkeypatch.setattr(controller, "current_user", session)
    monkeypatch.setattr(service, "current_user", session)
    monkeypatch.setattr(User, "get", AsyncMock(return_value={"nickname": "旧昵称"}))
    monkeypatch.setattr(User, "get_user_by_nickname", AsyncMock(return_value=None))
    monkeypatch.setattr(UserRole, "get_role_ids_by_user", AsyncMock(return_value=[3]))
    replace_roles = AsyncMock()
    monkeypatch.setattr(UserRole, "set_user_roles", replace_roles)
    redis = SimpleNamespace(set=AsyncMock())
    monkeypatch.setattr(service, "redis_pool", SimpleNamespace(redis=redis))
    payload = {
        "id": 42,
        "username": "test-user",
        "nickname": "测试账号",
        "avatar": "",
        "remarks": "",
        "email": "",
        "tags": ["测试"],
    }
    update = AsyncMock(return_value=dict(payload))
    monkeypatch.setattr(User, "update", update)

    response = await controller.save_or_update(UserIn(**payload))

    assert response.status_code == 200
    update.assert_awaited_once_with(payload, to_dict=True)
    replace_roles.assert_not_awaited()
    assert redis.set.await_args.args[1]["roles"] == [3]
