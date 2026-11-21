from pydantic import BaseModel


class DictItem(BaseModel):
    """字典表通用返回项：分类 / 成色 / 交易地点共用。"""
    id: int
    name: str
    sort_order: int
