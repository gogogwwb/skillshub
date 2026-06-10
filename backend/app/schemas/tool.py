from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class ToolBase(BaseModel):
    name: str
    description: Optional[str] = None
    skill_id: Optional[int] = None
    parameters: Optional[Any] = None
    endpoint: Optional[str] = None
    method: str = "POST"


class ToolCreate(ToolBase):
    pass


class ToolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    skill_id: Optional[int] = None
    parameters: Optional[Any] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status: Optional[str] = None


class ToolRead(ToolBase):
    id: int
    status: str = "active"
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ToolBrief(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class ToolWithPermission(ToolRead):
    has_permission: bool = False
    skill_name: Optional[str] = None

    model_config = {"from_attributes": True}
