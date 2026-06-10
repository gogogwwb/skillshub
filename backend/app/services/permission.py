from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import PermissionRequest, User, Skill, Tool
from app.schemas.permission import PermissionRequestCreate
from typing import Optional
from datetime import datetime, timezone


class PermissionService:
    """权限申请与审批服务"""

    @staticmethod
    def create_request(db: Session, user_id: int, data: PermissionRequestCreate) -> PermissionRequest:
        """创建权限申请"""
        # 检查是否已有相同申请
        existing = db.query(PermissionRequest).filter(
            PermissionRequest.user_id == user_id,
            PermissionRequest.type == data.type,
            PermissionRequest.target_id == data.target_id,
            PermissionRequest.status == "pending",
        ).first()
        if existing:
            raise ValueError("A pending request already exists for this resource")

        # 检查目标是否存在
        if data.type == "skill":
            target = db.query(Skill).filter(Skill.id == data.target_id).first()
        else:
            target = db.query(Tool).filter(Tool.id == data.target_id).first()
        if not target:
            raise ValueError(f"{data.type} with id {data.target_id} not found")

        req = PermissionRequest(
            user_id=user_id,
            type=data.type,
            target_id=data.target_id,
            reason=data.reason,
            status="pending",
        )
        db.add(req)
        db.commit()
        db.refresh(req)
        return req

    @staticmethod
    def get_my_requests(
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[PermissionRequest], int]:
        query = db.query(PermissionRequest).filter(PermissionRequest.user_id == user_id)
        total = query.count()
        items = query.order_by(PermissionRequest.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    @staticmethod
    def cancel_request(db: Session, request_id: int, user_id: int) -> bool:
        req = db.query(PermissionRequest).filter(
            PermissionRequest.id == request_id,
            PermissionRequest.user_id == user_id,
        ).first()
        if not req:
            raise ValueError("Request not found")
        if req.status != "pending":
            raise ValueError("Only pending requests can be cancelled")
        req.status = "cancelled"
        db.commit()
        return True

    @staticmethod
    def get_pending_requests(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        status_filter: Optional[str] = None,
    ) -> tuple[list[PermissionRequest], int]:
        query = db.query(PermissionRequest)
        if status_filter:
            query = query.filter(PermissionRequest.status == status_filter)
        total = query.count()
        items = query.order_by(PermissionRequest.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    @staticmethod
    def approve_request(db: Session, request_id: int, reviewer_id: int, comment: Optional[str] = None) -> PermissionRequest:
        req = db.query(PermissionRequest).filter(PermissionRequest.id == request_id).first()
        if not req:
            raise ValueError("Request not found")
        if req.status != "pending":
            raise ValueError("Only pending requests can be approved")

        req.status = "approved"
        req.reviewed_by = reviewer_id
        req.review_comment = comment
        req.reviewed_at = datetime.now(timezone.utc)

        # 审批通过：为用户分配对应权限（通过分配到对应角色或直接关联）
        # 这里简化处理：将权限关联到用户的第一个角色，如果没有角色则创建一个默认角色
        user = db.query(User).filter(User.id == req.user_id).first()
        if user:
            if req.type == "skill":
                from app.models import RoleSkill
                # 查找用户是否已有角色包含此skill
                has_skill = False
                for role in user.roles:
                    if any(s.id == req.target_id for s in role.skills):
                        has_skill = True
                        break
                if not has_skill:
                    # 使用用户第一个角色或创建默认角色
                    role = user.roles[0] if user.roles else _get_or_create_default_role(db, user.id)
                    if not any(rs.skill_id == req.target_id for rs in role.skills if hasattr(rs, 'skill_id')):
                        db.add(RoleSkill(role_id=role.id, skill_id=req.target_id))
            elif req.type == "tool":
                from app.models import RoleTool
                has_tool = False
                for role in user.roles:
                    if any(t.id == req.target_id for t in role.tools):
                        has_tool = True
                        break
                if not has_tool:
                    role = user.roles[0] if user.roles else _get_or_create_default_role(db, user.id)
                    db.add(RoleTool(role_id=role.id, tool_id=req.target_id))

        db.commit()
        db.refresh(req)
        return req

    @staticmethod
    def reject_request(db: Session, request_id: int, reviewer_id: int, comment: Optional[str] = None) -> PermissionRequest:
        req = db.query(PermissionRequest).filter(PermissionRequest.id == request_id).first()
        if not req:
            raise ValueError("Request not found")
        if req.status != "pending":
            raise ValueError("Only pending requests can be rejected")

        req.status = "rejected"
        req.reviewed_by = reviewer_id
        req.review_comment = comment
        req.reviewed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(req)
        return req

    @staticmethod
    def verify_permission(db: Session, user_id: int, perm_type: str, target_name: str) -> dict:
        """验证用户是否有权限"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user or user.status != "active":
            return {"allowed": False, "user_id": user_id, "type": perm_type, "target_name": target_name, "reason": "User not found or inactive"}

        if perm_type == "skill":
            for role in user.roles:
                for skill in role.skills:
                    if skill.name == target_name and skill.status == "active":
                        return {"allowed": True, "user_id": user_id, "type": perm_type, "target_name": target_name}
        elif perm_type == "tool":
            for role in user.roles:
                for tool in role.tools:
                    if tool.name == target_name and tool.status == "active":
                        return {"allowed": True, "user_id": user_id, "type": perm_type, "target_name": target_name}

        return {"allowed": False, "user_id": user_id, "type": perm_type, "target_name": target_name, "reason": "No matching permission found"}


def _get_or_create_default_role(db: Session, user_id: int):
    """为用户获取或创建默认角色"""
    from app.models import Role, UserRole
    role_name = f"user_{user_id}_default"
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        role = Role(name=role_name, description=f"Auto-created default role for user {user_id}")
        db.add(role)
        db.flush()
        db.add(UserRole(user_id=user_id, role_id=role.id))
        db.flush()
    return role


permission_service = PermissionService()
