from sqlalchemy.orm import Session
from app.models import Role, RoleSkill, RoleTool
from app.schemas.role import RoleCreate, RoleUpdate
from typing import Optional


class RoleService:
    """角色服务"""

    @staticmethod
    def get_role_list(db: Session) -> list[Role]:
        return db.query(Role).all()

    @staticmethod
    def get_role_detail(db: Session, role_id: int) -> Optional[Role]:
        return db.query(Role).filter(Role.id == role_id).first()

    @staticmethod
    def create_role(db: Session, data: RoleCreate) -> Role:
        role = Role(name=data.name, description=data.description)
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def update_role(db: Session, role_id: int, data: RoleUpdate) -> Role:
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError("Role not found")
        if data.name is not None:
            role.name = data.name
        if data.description is not None:
            role.description = data.description
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def delete_role(db: Session, role_id: int) -> bool:
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError("Role not found")
        db.delete(role)
        db.commit()
        return True

    @staticmethod
    def assign_skills(db: Session, role_id: int, skill_ids: list[int]) -> Role:
        """分配技能权限给角色"""
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError("Role not found")

        db.query(RoleSkill).filter(RoleSkill.role_id == role_id).delete()
        for skill_id in skill_ids:
            db.add(RoleSkill(role_id=role_id, skill_id=skill_id))
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def assign_tools(db: Session, role_id: int, tool_ids: list[int]) -> Role:
        """分配工具权限给角色"""
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError("Role not found")

        db.query(RoleTool).filter(RoleTool.role_id == role_id).delete()
        for tool_id in tool_ids:
            db.add(RoleTool(role_id=role_id, tool_id=tool_id))
        db.commit()
        db.refresh(role)
        return role


role_service = RoleService()
