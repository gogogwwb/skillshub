from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import User, UserRole, Role
from app.schemas.user import UserRead, UserRoleUpdate
from typing import Optional


class UserService:
    """用户服务"""

    @staticmethod
    def get_user_list(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
    ) -> tuple[list[User], int]:
        query = db.query(User)
        if keyword:
            query = query.filter(
                or_(
                    User.name.contains(keyword),
                    User.email.contains(keyword),
                )
            )
        total = query.count()
        users = query.offset((page - 1) * page_size).limit(page_size).all()
        return users, total

    @staticmethod
    def get_user_detail(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def update_user_roles(db: Session, user_id: int, role_ids: list[int]) -> User:
        """更新用户角色"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # 删除旧角色关联
        db.query(UserRole).filter(UserRole.user_id == user_id).delete()

        # 添加新角色关联
        for role_id in role_ids:
            role = db.query(Role).filter(Role.id == role_id).first()
            if role:
                db.add(UserRole(user_id=user_id, role_id=role_id))

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user_status(db: Session, user_id: int, status: str) -> User:
        """更新用户状态"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        user.status = status
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_permissions(db: Session, user_id: int) -> dict:
        """获取用户权限(通过角色获取skills和tools)"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"skills": [], "tools": []}

        skill_names = set()
        tool_names = set()
        for role in user.roles:
            for skill in role.skills:
                if skill.status == "active":
                    skill_names.add(skill.name)
            for tool in role.tools:
                if tool.status == "active":
                    tool_names.add(tool.name)

        return {"skills": list(skill_names), "tools": list(tool_names)}


user_service = UserService()
