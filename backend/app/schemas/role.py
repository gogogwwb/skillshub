from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class RoleRead(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    skills: list["SkillBrief"] = []
    tools: list["ToolBrief"] = []

    model_config = {"from_attributes": True}


class RoleSkillAssign(BaseModel):
    skill_ids: list[int]


class RoleToolAssign(BaseModel):
    tool_ids: list[int]


# Forward references
from app.schemas.skill import SkillBrief  # noqa: E402
from app.schemas.tool import ToolBrief  # noqa: E402

RoleRead.model_rebuild()
