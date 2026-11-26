from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class UserStatusIn(BaseModel):
    """管理员封禁/解封用户：0 封禁，1 正常。"""
    status: Literal[0, 1] = Field(..., description="目标状态：0 封禁、1 解封")


class AdminLogItem(BaseModel):
    """一条管理员操作日志；触发器自动审计的记录 admin_id 为空。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    admin_id: int | None = None
    action: str
    target_type: str
    target_id: int
    detail: str | None = None
    created_at: datetime


class AdminLogListOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[AdminLogItem]
