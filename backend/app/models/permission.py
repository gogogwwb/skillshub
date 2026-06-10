from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base


class PermissionRequest(Base):
    __tablename__ = "permission_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="申请人ID")
    type = Column(SQLEnum("skill", "tool", name="request_type"), nullable=False, comment="申请类型")
    target_id = Column(Integer, nullable=False, comment="目标ID(skill或tool的ID)")
    reason = Column(Text, nullable=True, comment="申请理由")
    status = Column(
        SQLEnum("pending", "approved", "rejected", "cancelled", name="request_status"),
        default="pending",
        comment="申请状态",
    )
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="审批人ID")
    review_comment = Column(Text, nullable=True, comment="审批备注")
    reviewed_at = Column(DateTime, nullable=True, comment="审批时间")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id], back_populates="permission_requests")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
