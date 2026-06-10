from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    feishu_id = Column(String(64), unique=True, nullable=True, index=True, comment="飞书部门ID")
    name = Column(String(128), nullable=False, comment="部门名称")
    parent_id = Column(Integer, ForeignKey("departments.id"), nullable=True, comment="父部门ID")
    path = Column(String(512), nullable=True, comment="部门路径(如: /总部/技术部/后端组)")
    status = Column(SQLEnum("active", "inactive", name="department_status"), default="active", comment="状态")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    parent = relationship("Department", remote_side=[id], backref="children")
    users = relationship("User", back_populates="department")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    feishu_id = Column(String(64), unique=True, nullable=True, index=True, comment="飞书用户ID")
    name = Column(String(128), nullable=False, comment="用户名")
    email = Column(String(256), nullable=True, comment="邮箱")
    avatar = Column(String(512), nullable=True, comment="头像URL")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, comment="部门ID")
    status = Column(SQLEnum("active", "inactive", name="user_status"), default="active", comment="状态")
    is_admin = Column(Boolean, default=False, comment="是否管理员")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    department = relationship("Department", back_populates="users")
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    permission_requests = relationship("PermissionRequest", foreign_keys="PermissionRequest.user_id", back_populates="user")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), unique=True, nullable=False, comment="角色名称")
    description = Column(String(256), nullable=True, comment="角色描述")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", secondary="user_roles", back_populates="roles")
    skills = relationship("Skill", secondary="role_skills", back_populates="roles")
    tools = relationship("Tool", secondary="role_tools", back_populates="roles")


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), unique=True, nullable=False, comment="技能名称")
    description = Column(Text, nullable=True, comment="技能描述")
    config = Column(JSON, nullable=True, comment="技能配置(JSON)")
    status = Column(SQLEnum("active", "inactive", name="skill_status"), default="active", comment="状态")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建人")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    roles = relationship("Role", secondary="role_skills", back_populates="skills")
    tools = relationship("Tool", back_populates="skill", cascade="all, delete-orphan")


class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=True, comment="所属技能ID")
    name = Column(String(128), unique=True, nullable=False, comment="工具名称")
    description = Column(Text, nullable=True, comment="工具描述")
    parameters = Column(JSON, nullable=True, comment="工具参数定义(JSON)")
    endpoint = Column(String(512), nullable=True, comment="工具调用端点")
    method = Column(String(10), default="POST", comment="调用方法(GET/POST)")
    status = Column(SQLEnum("active", "inactive", name="tool_status"), default="active", comment="状态")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建人")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    skill = relationship("Skill", back_populates="tools")
    roles = relationship("Role", secondary="role_tools", back_populates="tools")


class RoleSkill(Base):
    __tablename__ = "role_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class RoleTool(Base):
    __tablename__ = "role_tools"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    tool_id = Column(Integer, ForeignKey("tools.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
