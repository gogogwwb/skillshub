from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import success_response, error_response
from app.schemas.skill import SkillCreate, SkillUpdate
from app.middleware.auth import require_admin
from app.services.skill import skill_service
from app.services.audit import audit_service
from app.models import User

router = APIRouter()


@router.get("")
async def list_skills(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    status: str = Query(None),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get skill list"""
    skills, total = skill_service.get_skill_list(db, page, page_size, keyword, status)
    result = []
    for s in skills:
        result.append({
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "config": s.config,
            "status": s.status,
            "tool_count": len(s.tools) if s.tools else 0,
            "created_by": s.created_by,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        })
    return success_response(data={"items": result, "total": total, "page": page, "page_size": page_size})


@router.post("")
async def create_skill(
    data: SkillCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create skill"""
    try:
        skill = skill_service.create_skill(db, data, admin.id)
        audit_service.log(db, admin.id, "create", "skill", skill.id, {"name": data.name})
        return success_response(data={"id": skill.id, "name": skill.name})
    except Exception as e:
        return error_response(message=str(e))


@router.put("/{skill_id}")
async def update_skill(
    skill_id: int,
    data: SkillUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update skill"""
    try:
        skill = skill_service.update_skill(db, skill_id, data)
        audit_service.log(db, admin.id, "update", "skill", skill_id, data.model_dump(exclude_none=True))
        return success_response(message="Skill updated")
    except ValueError as e:
        return error_response(message=str(e))


@router.delete("/{skill_id}")
async def delete_skill(
    skill_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete skill"""
    try:
        skill_service.delete_skill(db, skill_id)
        audit_service.log(db, admin.id, "delete", "skill", skill_id)
        return success_response(message="Skill deleted")
    except ValueError as e:
        return error_response(message=str(e))
