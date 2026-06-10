from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import success_response
from app.middleware.auth import get_current_user
from app.services.skill import skill_service
from app.services.tool import tool_service
from app.models import User

router = APIRouter()


@router.get("")
async def list_skills(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List skills with permission status"""
    skills, total = skill_service.get_skill_list(db, page, page_size, keyword)
    user_skill_ids = skill_service.get_user_skill_ids(db, current_user.id)

    result = []
    for s in skills:
        item = {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "config": s.config,
            "status": s.status,
            "has_permission": s.id in user_skill_ids,
            "tool_count": len(s.tools) if s.tools else 0,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        }
        result.append(item)

    return success_response(data={"items": result, "total": total, "page": page, "page_size": page_size})


@router.get("/{skill_id}")
async def get_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get skill detail"""
    skill = skill_service.get_skill_detail(db, skill_id)
    if not skill:
        return success_response(data=None, message="Skill not found")
    user_skill_ids = skill_service.get_user_skill_ids(db, current_user.id)
    return success_response(data={
        "id": skill.id,
        "name": skill.name,
        "description": skill.description,
        "config": skill.config,
        "status": skill.status,
        "has_permission": skill.id in user_skill_ids,
        "created_at": skill.created_at.isoformat() if skill.created_at else None,
    })


@router.get("/{skill_id}/tools")
async def get_skill_tools(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List tools under a skill"""
    tools, total = tool_service.get_tool_list(db, skill_id=skill_id)
    user_tool_ids = tool_service.get_user_tool_ids(db, current_user.id)

    result = []
    for t in tools:
        result.append({
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "has_permission": t.id in user_tool_ids,
            "status": t.status,
        })

    return success_response(data=result)
