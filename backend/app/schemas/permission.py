from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PermissionRequestCreate(BaseModel):
    type: str  # skill / tool
    target_id: int
    reason: Optional[str] = None


class PermissionRequestRead(BaseModel):
    id: int
    user_id: int
    type: str
    target_id: int
    target_name: Optional[str] = None
    reason: Optional[str] = None
    status: str
    reviewed_by: Optional[int] = None
    reviewer_name: Optional[str] = None
    review_comment: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    user_name: Optional[str] = None

    model_config = {"from_attributes": True}


class ApprovalAction(BaseModel):
    comment: Optional[str] = None


class PermissionVerifyRequest(BaseModel):
    user_id: int
    type: str  # skill / tool
    target_name: str  # skill name or tool name


class PermissionVerifyResponse(BaseModel):
    allowed: bool
    user_id: int
    type: str
    target_name: str
    reason: Optional[str] = None

    model_config = {"from_attributes": True}


class UserPermissions(BaseModel):
    skills: list[str] = []  # skill names
    tools: list[str] = []   # tool names

    model_config = {"from_attributes": True}
