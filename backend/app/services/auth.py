from sqlalchemy.orm import Session
from app.models import User, Department
from app.utils.security import create_access_token
from app.services.feishu import feishu_service
from app.schemas.auth import TokenResponse
from app.config import settings
from typing import Optional


class AuthService:
    """认证服务"""

    @staticmethod
    def get_feishu_login_url(state: Optional[str] = None) -> str:
        return feishu_service.get_auth_url(state)

    @staticmethod
    async def handle_feishu_callback(code: str, db: Session) -> TokenResponse:
        """处理飞书OAuth2回调"""
        # 1. 用code换取user_access_token
        token_data = await feishu_service.get_user_access_token(code)

        # 2. 获取用户信息
        user_info = await feishu_service.get_user_info(token_data["access_token"])

        feishu_id = user_info.get("user_id") or user_info.get("open_id")
        name = user_info.get("name", "")
        email = user_info.get("email", "")
        avatar = user_info.get("avatar_url", "")
        department_ids = user_info.get("department_ids", [])

        # 3. 查找或创建用户
        user = db.query(User).filter(User.feishu_id == feishu_id).first()
        if user is None:
            # 创建新用户
            dept_id = None
            if department_ids:
                dept_feishu_id = department_ids[0]
                dept = db.query(Department).filter(Department.feishu_id == dept_feishu_id).first()
                if dept:
                    dept_id = dept.id

            user = User(
                feishu_id=feishu_id,
                name=name,
                email=email,
                avatar=avatar,
                department_id=dept_id,
                status="active",
                is_admin=False,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # 更新用户信息
            user.name = name
            user.email = email
            user.avatar = avatar
            if department_ids:
                dept_feishu_id = department_ids[0]
                dept = db.query(Department).filter(Department.feishu_id == dept_feishu_id).first()
                if dept:
                    user.department_id = dept.id
            db.commit()

        # 4. 生成JWT
        access_token = create_access_token(
            data={"user_id": user.id, "is_admin": user.is_admin}
        )

        return TokenResponse(
            access_token=access_token,
            user_id=user.id,
            name=user.name,
            is_admin=user.is_admin,
        )

    @staticmethod
    def dev_login(db: Session, username: str, is_admin: bool = False) -> TokenResponse:
        """开发模式登录（仅DEBUG=True时可用）"""
        if not settings.DEBUG:
            raise ValueError("Dev login is only available in DEBUG mode")

        # 优先按用户名查找已存在的用户，其次按feishu_id查找
        user = db.query(User).filter(User.name == username).first()
        if user is None:
            feishu_id = f"dev_{username}"
            user = db.query(User).filter(User.feishu_id == feishu_id).first()

        if user is None:
            # 创建新用户
            user = User(
                feishu_id=f"dev_{username}",
                name=username,
                email=f"{username}@dev.local",
                status="active",
                is_admin=is_admin,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # 更新管理员状态
            if user.is_admin != is_admin:
                user.is_admin = is_admin
                db.commit()

        access_token = create_access_token(
            data={"user_id": user.id, "is_admin": user.is_admin}
        )

        return TokenResponse(
            access_token=access_token,
            user_id=user.id,
            name=user.name,
            is_admin=user.is_admin,
        )


auth_service = AuthService()
