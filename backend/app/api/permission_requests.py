from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import success_response, error_response
from app.schemas.permission import PermissionRequestCreate
from app.middleware.auth import get_current_user
from app.services.permission import permission_service
from app.models import User, Skill, Tool

router = APIRouter()


@router.post("")
async def create_permission_request(
    data: PermissionRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """提交权限申请"""
    try:
        req = permission_service.create_request(db, current_user.id, data)
        return success_response(data={"id": req.id, "status": req.status})
    except ValueError as e:
        return error_response(message=str(e))


@router.get("")
async def list_my_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """我的申请列表"""
    items, total = permission_service.get_my_requests(db, current_user.id, page, page_size)

    result = []
    for item in items:
        target_name = None
        if item.type == "skill":
            skill = db.query(Skill).filter(Skill.id == item.target_id).first()
            target_name = skill.name if skill else None
        else:
            tool = db.query(Tool).filter(Tool.id == item.target_id).first()
            target_name = tool.name if tool else None

        result.append({
            "id": item.id,
            "type": item.type,
            "target_id": item.target_id,
            "target_name": target_name,
            "reason": item.reason,
            "status": item.status,
            "review_comment": item.review_comment,
            "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else None,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        })

    return success_response(data={"items": result, "total": total, "page": page, "page_size": page_size})


@router.get("/{request_id}")
async def get_request_detail(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """申请详情"""
    items, _ = permission_service.get_my_requests(db, current_user.id, 1, 1000)
    req = next((i for i in items if i.id == request_id), None)
    if not req:
        return error_response(message="Request not found")

    target_name = None
    if req.type == "skill":
        skill = db.query(Skill).filter(Skill.id == req.target_id).first()
        target_name = skill.name if skill else None
    else:
        tool = db.query(Tool).filter(Tool.id == req.target_id).first()
        target_name = tool.name if tool else None

    return success_response(data={
        "id": req.id,
        "type": req.type,
        "target_id": req.target_id,
        "target_name": target_name,
        "reason": req.reason,
        "status": req.status,
        "review_comment": req.review_comment,
        "reviewed_at": req.reviewed_at.isoformat() if req.reviewed_at else None,
        "created_at": req.created_at.isoformat() if req.created_at else None,
    })


@router.delete("/{request_id}")
async def cancel_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """撤销申请"""
    try:
        permission_service.cancel_request(db, request_id, current_user.id)
        return success_response(message="Request cancelled")
    except ValueError as e:
        return error_response(message=str(e))
