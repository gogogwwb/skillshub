"""
种子数据脚本 - 插入测试数据
运行方式: cd backend && python -m scripts.seed
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import (
    Department, User, Role, UserRole,
    Skill, Tool, RoleSkill, RoleTool,
)


def seed():
    db = SessionLocal()
    try:
        # === 部门 ===
        dept_tech = Department(name="技术部", path="/技术部", status="active")
        dept_product = Department(name="产品部", path="/产品部", status="active")
        db.add_all([dept_tech, dept_product])
        db.flush()

        # === 用户 ===
        admin = User(
            feishu_id="dev_admin", name="管理员",
            email="admin@dev.local", is_admin=True,
            department_id=dept_tech.id, status="active",
        )
        user1 = User(
            feishu_id="dev_zhangsan", name="张三",
            email="zhangsan@dev.local", is_admin=False,
            department_id=dept_tech.id, status="active",
        )
        user2 = User(
            feishu_id="dev_lisi", name="李四",
            email="lisi@dev.local", is_admin=False,
            department_id=dept_product.id, status="active",
        )
        db.add_all([admin, user1, user2])
        db.flush()

        # === Skills ===
        skill_doc = Skill(name="文档处理", description="处理各类文档的AI技能", status="active",
                          config={"model": "gpt-4", "temperature": 0.7})
        skill_code = Skill(name="代码生成", description="根据需求生成代码的AI技能", status="active",
                           config={"model": "gpt-4", "temperature": 0.3})
        skill_data = Skill(name="数据分析", description="数据清洗、统计与可视化的AI技能", status="active",
                           config={"model": "gpt-4", "temperature": 0.5})
        skill_translate = Skill(name="翻译助手", description="多语言翻译AI技能", status="active",
                                config={"model": "gpt-4", "temperature": 0.2})
        db.add_all([skill_doc, skill_code, skill_data, skill_translate])
        db.flush()

        # === Tools ===
        tools_data = [
            # 文档处理下的工具
            Tool(skill_id=skill_doc.id, name="pdf_reader", description="读取PDF文档内容",
                 parameters={"type": "object", "properties": {"file_path": {"type": "string"}}},
                 endpoint="/tools/pdf_reader", method="POST", status="active"),
            Tool(skill_id=skill_doc.id, name="docx_writer", description="生成Word文档",
                 parameters={"type": "object", "properties": {"template": {"type": "string"}, "data": {"type": "object"}}},
                 endpoint="/tools/docx_writer", method="POST", status="active"),
            Tool(skill_id=skill_doc.id, name="text_summarizer", description="文本摘要生成",
                 parameters={"type": "object", "properties": {"text": {"type": "string"}, "max_length": {"type": "integer"}}},
                 endpoint="/tools/text_summarizer", method="POST", status="active"),
            # 代码生成下的工具
            Tool(skill_id=skill_code.id, name="python_coder", description="生成Python代码",
                 parameters={"type": "object", "properties": {"requirement": {"type": "string"}, "framework": {"type": "string"}}},
                 endpoint="/tools/python_coder", method="POST", status="active"),
            Tool(skill_id=skill_code.id, name="sql_generator", description="根据自然语言生成SQL",
                 parameters={"type": "object", "properties": {"question": {"type": "string"}, "schema": {"type": "string"}}},
                 endpoint="/tools/sql_generator", method="POST", status="active"),
            Tool(skill_id=skill_code.id, name="code_reviewer", description="代码审查与优化建议",
                 parameters={"type": "object", "properties": {"code": {"type": "string"}, "language": {"type": "string"}}},
                 endpoint="/tools/code_reviewer", method="POST", status="active"),
            # 数据分析下的工具
            Tool(skill_id=skill_data.id, name="data_cleaner", description="数据清洗与预处理",
                 parameters={"type": "object", "properties": {"data_source": {"type": "string"}, "rules": {"type": "array"}}},
                 endpoint="/tools/data_cleaner", method="POST", status="active"),
            Tool(skill_id=skill_data.id, name="chart_generator", description="数据可视化图表生成",
                 parameters={"type": "object", "properties": {"data": {"type": "object"}, "chart_type": {"type": "string"}}},
                 endpoint="/tools/chart_generator", method="POST", status="active"),
            # 翻译助手下的工具
            Tool(skill_id=skill_translate.id, name="zh_en_translator", description="中英互译",
                 parameters={"type": "object", "properties": {"text": {"type": "string"}, "source_lang": {"type": "string"}, "target_lang": {"type": "string"}}},
                 endpoint="/tools/zh_en_translator", method="POST", status="active"),
        ]
        db.add_all(tools_data)
        db.flush()

        # === 角色 ===
        role_admin = Role(name="系统管理员", description="拥有所有权限")
        role_dev = Role(name="开发人员", description="开发相关技能和工具权限")
        role_analyst = Role(name="数据分析师", description="数据分析相关权限")
        role_viewer = Role(name="普通用户", description="基础浏览权限")
        db.add_all([role_admin, role_dev, role_analyst, role_viewer])
        db.flush()

        # === 角色-Skills关联 ===
        # 管理员拥有所有技能
        for s in [skill_doc, skill_code, skill_data, skill_translate]:
            db.add(RoleSkill(role_id=role_admin.id, skill_id=s.id))
        # 开发人员: 代码生成 + 文档处理
        for s in [skill_code, skill_doc]:
            db.add(RoleSkill(role_id=role_dev.id, skill_id=s.id))
        # 数据分析师: 数据分析 + 翻译助手
        for s in [skill_data, skill_translate]:
            db.add(RoleSkill(role_id=role_analyst.id, skill_id=s.id))
        # 普通用户: 翻译助手
        db.add(RoleSkill(role_id=role_viewer.id, skill_id=skill_translate.id))

        # === 角色-Tools关联 ===
        # 管理员拥有所有工具
        for t in tools_data:
            db.add(RoleTool(role_id=role_admin.id, tool_id=t.id))
        # 开发人员: 代码生成工具 + 文档处理工具
        dev_tools = [t for t in tools_data if t.skill_id in (skill_code.id, skill_doc.id)]
        for t in dev_tools:
            db.add(RoleTool(role_id=role_dev.id, tool_id=t.id))
        # 数据分析师: 数据分析工具 + 翻译工具
        analyst_tools = [t for t in tools_data if t.skill_id in (skill_data.id, skill_translate.id)]
        for t in analyst_tools:
            db.add(RoleTool(role_id=role_analyst.id, tool_id=t.id))
        # 普通用户: 翻译工具
        viewer_tools = [t for t in tools_data if t.skill_id == skill_translate.id]
        for t in viewer_tools:
            db.add(RoleTool(role_id=role_viewer.id, tool_id=t.id))

        # === 用户-角色关联 ===
        db.add(UserRole(user_id=admin.id, role_id=role_admin.id))
        db.add(UserRole(user_id=user1.id, role_id=role_dev.id))
        db.add(UserRole(user_id=user2.id, role_id=role_analyst.id))

        db.commit()

        print("=== 种子数据插入完成 ===")
        print(f"部门: {2} 个")
        print(f"用户: admin(管理员), 张三(开发人员), 李四(数据分析师)")
        print(f"技能: {4} 个 (文档处理, 代码生成, 数据分析, 翻译助手)")
        print(f"工具: {len(tools_data)} 个")
        print(f"角色: {4} 个 (系统管理员, 开发人员, 数据分析师, 普通用户)")
        print()

    except Exception as e:
        db.rollback()
        print(f"种子数据插入失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
