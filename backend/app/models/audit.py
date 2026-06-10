from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="操作人ID")
    action = Column(String(64), nullable=False, comment="操作类型(create/update/delete/approve/reject/login)")
    target_type = Column(String(64), nullable=True, comment="目标类型(user/role/skill/tool/permission_request)")
    target_id = Column(Integer, nullable=True, comment="目标ID")
    detail = Column(JSON, nullable=True, comment="操作详情(JSON)")
    ip_address = Column(String(45), nullable=True, comment="IP地址")
    created_at = Column(DateTime, default=datetime.utcnow)
