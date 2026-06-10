from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DepartmentBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    path: Optional[str] = None


class DepartmentRead(DepartmentBase):
    id: int
    feishu_id: Optional[str] = None
    status: str = "active"
    created_at: datetime

    model_config = {"from_attributes": True}


class DepartmentTree(DepartmentRead):
    children: list["DepartmentTree"] = []

    model_config = {"from_attributes": True}


class UserBase(BaseModel):
    name: str
    email: Optional[str] = None
    avatar: Optional[str] = None


class UserRead(UserBase):
    id: int
    feishu_id: Optional[str] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    status: str = "active"
    is_admin: bool = False
    created_at: datetime
    roles: list["RoleRead"] = []

    model_config = {"from_attributes": True}


class UserBrief(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    avatar: Optional[str] = None

    model_config = {"from_attributes": True}


class UserRoleUpdate(BaseModel):
    role_ids: list[int]


class UserStatusUpdate(BaseModel):
    status: str  # active / inactive


# Forward reference - RoleRead will be defined in role.py
from app.schemas.role import RoleRead  # noqa: E402

UserRead.model_rebuild()
