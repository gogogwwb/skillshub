from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Tool, Skill
from app.schemas.tool import ToolCreate, ToolUpdate
from typing import Optional


class ToolService:
    """工具服务"""

    @staticmethod
    def get_tool_list(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        skill_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> tuple[list[Tool], int]:
        query = db.query(Tool)
        if keyword:
            query = query.filter(
                or_(
                    Tool.name.contains(keyword),
                    Tool.description.contains(keyword),
                )
            )
        if skill_id:
            query = query.filter(Tool.skill_id == skill_id)
        if status:
            query = query.filter(Tool.status == status)
        total = query.count()
        tools = query.offset((page - 1) * page_size).limit(page_size).all()
        return tools, total

    @staticmethod
    def get_tool_detail(db: Session, tool_id: int) -> Optional[Tool]:
        return db.query(Tool).filter(Tool.id == tool_id).first()

    @staticmethod
    def create_tool(db: Session, data: ToolCreate, created_by: Optional[int] = None) -> Tool:
        tool = Tool(
            name=data.name,
            description=data.description,
            skill_id=data.skill_id,
            parameters=data.parameters,
            endpoint=data.endpoint,
            method=data.method,
            created_by=created_by,
        )
        db.add(tool)
        db.commit()
        db.refresh(tool)
        return tool

    @staticmethod
    def update_tool(db: Session, tool_id: int, data: ToolUpdate) -> Tool:
        tool = db.query(Tool).filter(Tool.id == tool_id).first()
        if not tool:
            raise ValueError("Tool not found")
        if data.name is not None:
            tool.name = data.name
        if data.description is not None:
            tool.description = data.description
        if data.skill_id is not None:
            tool.skill_id = data.skill_id
        if data.parameters is not None:
            tool.parameters = data.parameters
        if data.endpoint is not None:
            tool.endpoint = data.endpoint
        if data.method is not None:
            tool.method = data.method
        if data.status is not None:
            tool.status = data.status
        db.commit()
        db.refresh(tool)
        return tool

    @staticmethod
    def delete_tool(db: Session, tool_id: int) -> bool:
        tool = db.query(Tool).filter(Tool.id == tool_id).first()
        if not tool:
            raise ValueError("Tool not found")
        db.delete(tool)
        db.commit()
        return True

    @staticmethod
    def get_user_tool_ids(db: Session, user_id: int) -> set[int]:
        """获取用户有权限的工具ID集合"""
        from app.models import User
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return set()
        tool_ids = set()
        for role in user.roles:
            for tool in role.tools:
                if tool.status == "active":
                    tool_ids.add(tool.id)
        return tool_ids


tool_service = ToolService()
