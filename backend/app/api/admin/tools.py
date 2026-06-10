from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import success_response, error_response
from app.schemas.tool import ToolCreate, ToolUpdate
from app.middleware.auth import require_admin
from app.services.tool import tool_service
from app.services.audit import audit_service
from app.models import User

router = APIRouter()


@router.get("")
async def list_tools(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    skill_id: int = Query(None),
    status: str = Query(None),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取工具列表"""
    tools, total = tool_service.get_tool_list(db, page, page_size, keyword, skill_id, status)
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
            "created_by": t.created_by,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        })
    return success_response(data={"items": result, "total": total, "page": page, "page_size": page_size})


@router.post("")
async def create_tool(
    data: ToolCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """创建工具"""
    try:
        tool = tool_service.create_tool(db, data, admin.id)
        audit_service.log(db, admin.id, "create", "tool", tool.id, {"name": data.name})
        return success_response(data={"id": tool.id, "name": tool.name})
    except Exception as e:
        return error_response(message=str(e))


@router.put("/{tool_id}")
async def update_tool(
    tool_id: int,
    data: ToolUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """更新工具"""
    try:
        tool = tool_service.update_tool(db, tool_id, data)
        audit_service.log(db, admin.id, "update", "tool", tool_id, data.model_dump(exclude_none=True))
        return success_response(message="Tool updated")
    except ValueError as e:
        return error_response(message=str(e))


@router.delete("/{tool_id}")
async def delete_tool(
    tool_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """删除工具"""
    try:
        tool_service.delete_tool(db, tool_id)
        audit_service.log(db, admin.id, "delete", "tool", tool_id)
        return success_response(message="Tool deleted")
    except ValueError as e:
        return error_response(message=str(e))
