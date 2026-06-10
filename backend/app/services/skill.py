from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Skill, Tool
from app.schemas.skill import SkillCreate, SkillUpdate
from typing import Optional


class SkillService:
    """技能服务"""

    @staticmethod
    def get_skill_list(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
    ) -> tuple[list[Skill], int]:
        query = db.query(Skill)
        if keyword:
            query = query.filter(
                or_(
                    Skill.name.contains(keyword),
                    Skill.description.contains(keyword),
                )
            )
        if status:
            query = query.filter(Skill.status == status)
        total = query.count()
        skills = query.offset((page - 1) * page_size).limit(page_size).all()
        return skills, total

    @staticmethod
    def get_skill_detail(db: Session, skill_id: int) -> Optional[Skill]:
        return db.query(Skill).filter(Skill.id == skill_id).first()

    @staticmethod
    def create_skill(db: Session, data: SkillCreate, created_by: Optional[int] = None) -> Skill:
        skill = Skill(
            name=data.name,
            description=data.description,
            config=data.config,
            created_by=created_by,
        )
        db.add(skill)
        db.commit()
        db.refresh(skill)
        return skill

    @staticmethod
    def update_skill(db: Session, skill_id: int, data: SkillUpdate) -> Skill:
        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            raise ValueError("Skill not found")
        if data.name is not None:
            skill.name = data.name
        if data.description is not None:
            skill.description = data.description
        if data.config is not None:
            skill.config = data.config
        if data.status is not None:
            skill.status = data.status
        db.commit()
        db.refresh(skill)
        return skill

    @staticmethod
    def delete_skill(db: Session, skill_id: int) -> bool:
        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            raise ValueError("Skill not found")
        db.delete(skill)
        db.commit()
        return True

    @staticmethod
    def get_user_skill_ids(db: Session, user_id: int) -> set[int]:
        """获取用户有权限的技能ID集合"""
        from app.models import User
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return set()
        skill_ids = set()
        for role in user.roles:
            for skill in role.skills:
                if skill.status == "active":
                    skill_ids.add(skill.id)
        return skill_ids


skill_service = SkillService()
