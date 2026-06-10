from sqlalchemy.orm import Session
from app.models import AuditLog
from typing import Optional, Any


class AuditService:
    """审计日志服务"""

    @staticmethod
    def log(
        db: Session,
        user_id: Optional[int] = None,
        action: str = "",
        target_type: Optional[str] = None,
        target_id: Optional[int] = None,
        detail: Optional[Any] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
            ip_address=ip_address,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def get_logs(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        action: Optional[str] = None,
        target_type: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> tuple[list[AuditLog], int]:
        query = db.query(AuditLog)
        if action:
            query = query.filter(AuditLog.action == action)
        if target_type:
            query = query.filter(AuditLog.target_type == target_type)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        total = query.count()
        logs = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return logs, total


audit_service = AuditService()
