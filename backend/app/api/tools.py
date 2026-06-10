from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import success_response
from app.middleware.auth import get_current_user
from app.services.tool import tool_service
from app.models import User

router = APIRouter()


@router.get("")
async def list_tools(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    skill_id: int = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get tool list (with permission status)"""
    tools, total = tool_service.get_tool_list(db, page, page_size, keyword, skill_id)
    user_tool_ids = tool_service.get_user_tool_ids(db, current_user.id)

    result = []
    for t in tools:
        result.append({
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "skill_id": t.skill_id,
            "skill_name": t.skill.name if t.skill else None,
            "parameters": t.parameters,
            "endpoint": t.endpoint,
            "method": t.method,
            "status": t.status,
            "has_permission": t.id in user_tool_ids,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        })

    return success_response(data={"items": result, "total": total, "page": page, "page_size": page_size})


@router.get("/{tool_id}")
async def get_tool(
    tool_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get tool detail"""
    tool = tool_service.get_tool_detail(db, tool_id)
    if not tool:
        return success_response(data=None, message="Tool not found")
    user_tool_ids = tool_service.get_user_tool_ids(db, current_user.id)
    return success_response(data={
        "id": tool.id,
        "name": tool.name,
        "description": tool.description,
        "skill_id": tool.skill_id,
        "skill_name": tool.skill.name if tool.skill else None,
        "parameters": tool.parameters,
        "endpoint": tool.endpoint,
        "method": tool.method,
        "status": tool.status,
        "has_permission": tool.id in user_tool_ids,
        "created_at": tool.created_at.isoformat() if tool.created_at else None,
    })
