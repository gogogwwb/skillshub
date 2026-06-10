from sqlalchemy.orm import Session
from app.models import Department
from app.services.feishu import feishu_service
from typing import Optional


class DepartmentService:
    """部门服务 - 飞书组织架构同步"""

    @staticmethod
    def get_department_tree(db: Session) -> list[dict]:
        """获取部门树形结构"""
        departments = db.query(Department).filter(Department.status == "active").all()
        dept_map = {d.id: {"id": d.id, "feishu_id": d.feishu_id, "name": d.name, "parent_id": d.parent_id, "path": d.path, "children": []} for d in departments}

        tree = []
        for dept in departments:
            node = dept_map[dept.id]
            if dept.parent_id and dept.parent_id in dept_map:
                dept_map[dept.parent_id]["children"].append(node)
            else:
                tree.append(node)

        return tree

    @staticmethod
    async def sync_from_feishu(db: Session) -> dict:
        """从飞书同步组织架构"""
        synced_count = 0
        created_count = 0

        # 获取飞书根部门下的子部门
        await _sync_department_recursive(db, "0", None, "")
        db.commit()

        return {"message": "Sync completed", "synced": synced_count, "created": created_count}


async def _sync_department_recursive(
    db: Session,
    feishu_parent_id: str,
    db_parent_id: Optional[int],
    path_prefix: str,
):
    """递归同步飞书部门"""
    departments = await feishu_service.get_department_list(feishu_parent_id)

    for dept_data in departments:
        feishu_id = dept_data.get("department_id") or dept_data.get("open_department_id")
        name = dept_data.get("name", "")
        path = f"{path_prefix}/{name}"

        # 查找或创建部门
        dept = db.query(Department).filter(Department.feishu_id == feishu_id).first()
        if dept is None:
            dept = Department(
                feishu_id=feishu_id,
                name=name,
                parent_id=db_parent_id,
                path=path,
                status="active",
            )
            db.add(dept)
            db.flush()
        else:
            dept.name = name
            dept.parent_id = db_parent_id
            dept.path = path
            db.flush()

        # 递归同步子部门
        await _sync_department_recursive(db, feishu_id, dept.id, path)


department_service = DepartmentService()
