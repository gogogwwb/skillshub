from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import success_response
from app.middleware.auth import require_admin
from app.services.audit import audit_service
from app.models import User

router = APIRouter()


@router.get("")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    action: str = Query(None),
    target_type: str = Query(None),
    user_id: int = Query(None),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取审计日志列表"""
    logs, total = audit_service.get_logs(db, page, page_size, action, target_type, user_id)
    result = []
    for log in logs:
        result.append({
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "detail": log.detail,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        })
    return success_response(data={"items": result, "total": total, "page": page, "page_size": page_size})
