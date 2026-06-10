from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import success_response
from app.middleware.auth import require_admin
from app.services.department import department_service
from app.models import User

router = APIRouter()


@router.get("")
async def list_departments(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取部门树形列表"""
    tree = department_service.get_department_tree(db)
    return success_response(data=tree)


@router.post("/sync")
async def sync_departments(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """手动同步飞书组织架构"""
    try:
        result = await department_service.sync_from_feishu(db)
        return success_response(data=result)
    except Exception as e:
        return success_response(data={"error": str(e)}, message="Sync failed")
