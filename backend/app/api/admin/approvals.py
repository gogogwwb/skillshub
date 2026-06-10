from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import success_response, error_response
from app.schemas.permission import ApprovalAction
from app.middleware.auth import require_admin
from app.services.permission import permission_service
from app.services.audit import audit_service
from app.models import User, Skill, Tool

router = APIRouter()


@router.get("")
async def list_approvals(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取审批列表"""
    items, total = permission_service.get_pending_requests(db, page, page_size, status)
    result = []
    for item in items:
        target_name = None
        if item.type == "skill":
            skill = db.query(Skill).filter(Skill.id == item.target_id).first()
            target_name = skill.name if skill else None
        else:
            tool = db.query(Tool).filter(Tool.id == item.target_id).first()
            target_name = tool.name if tool else None

        reviewer_name = None
        if item.reviewed_by:
            reviewer = db.query(User).filter(User.id == item.reviewed_by).first()
            reviewer_name = reviewer.name if reviewer else None

        result.append({
            "id": item.id,
            "user_id": item.user_id,
            "user_name": item.user.name if item.user else None,
            "type": item.type,
            "target_id": item.target_id,
            "target_name": target_name,
            "reason": item.reason,
            "status": item.status,
            "reviewed_by": item.reviewed_by,
            "reviewer_name": reviewer_name,
            "review_comment": item.review_comment,
            "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else None,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        })

    return success_response(data={"items": result, "total": total, "page": page, "page_size": page_size})


@router.put("/{request_id}/approve")
async def approve_request(
    request_id: int,
    data: ApprovalAction,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """审批通过"""
    try:
        req = permission_service.approve_request(db, request_id, admin.id, data.comment)
        audit_service.log(db, admin.id, "approve", "permission_request", request_id, {"comment": data.comment})
        return success_response(message="Request approved")
    except ValueError as e:
        return error_response(message=str(e))


@router.put("/{request_id}/reject")
async def reject_request(
    request_id: int,
    data: ApprovalAction,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """审批拒绝"""
    try:
        req = permission_service.reject_request(db, request_id, admin.id, data.comment)
        audit_service.log(db, admin.id, "reject", "permission_request", request_id, {"comment": data.comment})
        return success_response(message="Request rejected")
    except ValueError as e:
        return error_response(message=str(e))
