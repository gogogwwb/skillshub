from pydantic import BaseModel
from typing import Optional


class TokenData(BaseModel):
    user_id: int
    is_admin: bool = False


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    is_admin: bool


class FeishuAuthURL(BaseModel):
    url: str


class DevLoginRequest(BaseModel):
    """开发模式登录请求"""
    username: str
    is_admin: bool = False
