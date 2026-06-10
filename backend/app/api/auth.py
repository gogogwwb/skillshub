from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import success_response, error_response
from app.schemas.auth import FeishuAuthURL, DevLoginRequest
from app.services.auth import auth_service
from app.middleware.auth import get_current_user
from app.models import User

router = APIRouter()


@router.get("/feishu/login")
async def feishu_login():
    """获取飞书OAuth2授权URL"""
    url = auth_service.get_feishu_login_url()
    return success_response(data={"url": url})


@router.get("/feishu/callback")
async def feishu_callback(code: str = Query(...), db: Session = Depends(get_db)):
    """飞书OAuth2回调处理"""
    try:
        token_response = await auth_service.handle_feishu_callback(code, db)
        return success_response(data=token_response.model_dump())
    except Exception as e:
        return error_response(message=str(e))


@router.post("/dev-login")
async def dev_login(data: DevLoginRequest, db: Session = Depends(get_db)):
    """开发模式登录(仅DEBUG=True时可用,跳过飞书认证)"""
    try:
        token_response = auth_service.dev_login(db, data.username, data.is_admin)
        return success_response(data=token_response.model_dump())
    except ValueError as e:
        return error_response(message=str(e))


@router.post("/logout")
async def logout():
    """登出(前端清除token即可)"""
    return success_response(message="Logged out successfully")


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return success_response(data={
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "avatar": current_user.avatar,
        "is_admin": current_user.is_admin,
        "status": current_user.status,
        "department_id": current_user.department_id,
    })
