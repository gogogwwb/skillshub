from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class SkillBase(BaseModel):
    name: str
    description: Optional[str] = None
    config: Optional[Any] = None


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Any] = None
    status: Optional[str] = None


class SkillRead(SkillBase):
    id: int
    status: str = "active"
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SkillBrief(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class SkillWithPermission(SkillRead):
    has_permission: bool = False
    tool_count: int = 0

    model_config = {"from_attributes": True}
