# ToolHub - AI Skills & Tools 权限管理系统

对企业内部的 AI Skills 及其对应的 Tools 进行权限管理，不同的人员和智能体只能调用有权限的 Tool。

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐
│  Client (React)  │    │  Admin (React)   │
│   端口: 5173/80  │    │   端口: 5174/81  │
└────────┬────────┘    └────────┬────────┘
         └──────────┬───────────┘
                    │
            ┌───────┴────────┐
            │ FastAPI Backend │
            │   端口: 8000    │
            ├────────────────┤
            │ Auth Module    │──→ 飞书OAuth2
            │ User Module    │──→ 组织架构同步
            │ Skill Module   │
            │ Tool Module    │
            │ Role Module    │
            │ Approval Module│
            │ Permission API │──→ 对外验证接口
            └───────┬────────┘
                    │
              ┌─────┴─────┐
              │   MySQL    │
              │  端口:3306 │
              └───────────┘
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| ORM | SQLAlchemy 2.0 |
| 数据库迁移 | Alembic |
| 数据库 | MySQL 8.0 |
| 认证 | JWT + 飞书OAuth2 |
| 前端框架 | React 19 + TypeScript |
| UI组件库 | Ant Design 5 |
| 状态管理 | Zustand |
| 构建工具 | Vite |
| 包管理 | uv (后端) / npm (前端) |
| 容器化 | Docker + docker-compose |

## 权限模型（RBAC）

```
用户 ──→ 角色 ──→ Skills / Tools
 │         │
 │    多对多关系
 │
 └── 一个用户可拥有多个角色
     权限 = UNION(用户所有角色关联的 Skills/Tools)
```

- 用户通过**角色**获得 Skills 和 Tools 的访问权限
- 角色可关联多个 Skills 和 Tools
- 用户可拥有多个角色
- 审批通过后自动分配权限

## 项目目录结构

```
toolhub/
├── pyproject.toml              # uv workspace 根配置
├── docker-compose.yml          # 容器编排
├── .env.example                # 环境变量模板
│
├── backend/                    # FastAPI 后端
│   ├── pyproject.toml          # 后端依赖（uv workspace member）
│   ├── Dockerfile
│   ├── alembic.ini             # 数据库迁移配置
│   ├── alembic/                # 迁移脚本
│   └── app/
│       ├── main.py             # FastAPI 应用入口
│       ├── config.py           # 配置管理（pydantic-settings）
│       ├── database.py         # SQLAlchemy 引擎与会话
│       ├── models/             # SQLAlchemy 数据模型
│       │   ├── user.py         #   Department, User, Role, UserRole, Skill, Tool, RoleSkill, RoleTool
│       │   ├── permission.py   #   PermissionRequest
│       │   └── audit.py        #   AuditLog
│       ├── schemas/            # Pydantic 请求/响应模型
│       │   ├── auth.py
│       │   ├── user.py
│       │   ├── role.py
│       │   ├── skill.py
│       │   ├── tool.py
│       │   ├── permission.py
│       │   └── common.py
│       ├── api/                # API 路由
│       │   ├── auth.py         #   飞书登录/回调/登出/当前用户
│       │   ├── users.py        #   客户端-用户权限查询
│       │   ├── skills.py       #   客户端-技能浏览
│       │   ├── tools.py        #   客户端-工具浏览
│       │   ├── permission_requests.py  # 客户端-权限申请
│       │   ├── admin/          #   管理端 API
│       │   │   ├── users.py    #     用户管理
│       │   │   ├── roles.py    #     角色管理+权限分配
│       │   │   ├── skills.py   #     技能 CRUD
│       │   │   ├── tools.py    #     工具 CRUD
│       │   │   ├── approvals.py#     审批管理
│       │   │   ├── departments.py#   部门管理+飞书同步
│       │   │   └── audit.py    #     审计日志
│       │   └── v1/
│       │       └── verify.py   #   对外权限验证 API
│       ├── services/           # 业务逻辑层
│       │   ├── feishu.py       #   飞书API调用
│       │   ├── auth.py         #   认证服务
│       │   ├── department.py   #   部门同步
│       │   ├── user.py         #   用户服务
│       │   ├── role.py         #   角色服务
│       │   ├── skill.py        #   技能服务
│       │   ├── tool.py         #   工具服务
│       │   ├── permission.py   #   权限申请/审批
│       │   └── audit.py        #   审计日志
│       ├── middleware/
│       │   └── auth.py         # JWT 认证中间件
│       └── utils/
│           └── security.py     # JWT 工具函数
│
└── frontend/
    ├── client/                 # 客户端 React 应用
    │   ├── package.json
    │   ├── Dockerfile
    │   ├── nginx.conf
    │   └── src/
    │       ├── App.tsx          # 路由配置
    │       ├── api/             # API 封装
    │       ├── store/           # Zustand 状态管理
    │       ├── components/      # 布局组件
    │       └── pages/           # 页面
    │           ├── Login.tsx
    │           ├── Dashboard.tsx
    │           ├── Skills.tsx
    │           ├── SkillDetail.tsx
    │           ├── Tools.tsx
    │           ├── ToolDetail.tsx
    │           ├── ApplyPermission.tsx
    │           └── MyRequests.tsx
    │
    └── admin/                  # 管理端 React 应用
        ├── package.json
        ├── Dockerfile
        ├── nginx.conf
        └── src/
            ├── App.tsx
            ├── api/
            ├── store/
            ├── components/
            └── pages/
                ├── Login.tsx
                ├── Dashboard.tsx
                ├── Users.tsx
                ├── Roles.tsx
                ├── Skills.tsx
                ├── Tools.tsx
                ├── Approvals.tsx
                ├── Departments.tsx
                └── AuditLogs.tsx
```

## API 概览

### 认证 `/api/auth`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /feishu/login | 获取飞书OAuth2授权URL |
| GET | /feishu/callback | 飞书回调处理 |
| POST | /logout | 登出 |
| GET | /me | 当前用户信息 |

### 客户端 API
| 模块 | 路径前缀 | 说明 |
|------|---------|------|
| 用户 | /api/users | 权限列表、角色列表 |
| 技能 | /api/skills | 技能浏览（含权限状态）、详情、关联工具 |
| 工具 | /api/tools | 工具浏览（含权限状态）、详情 |
| 权限申请 | /api/permission-requests | 提交申请、我的申请、撤销 |

### 管理端 API
| 模块 | 路径前缀 | 说明 |
|------|---------|------|
| 用户管理 | /api/admin/users | 用户列表、角色分配、启用/禁用 |
| 角色管理 | /api/admin/roles | 角色 CRUD、Skills/Tools 权限分配 |
| 技能管理 | /api/admin/skills | 技能 CRUD |
| 工具管理 | /api/admin/tools | 工具 CRUD |
| 审批管理 | /api/admin/approvals | 待审批列表、通过/拒绝 |
| 部门管理 | /api/admin/departments | 部门树、飞书同步 |
| 审计日志 | /api/admin/audit-logs | 操作记录查询 |

### 对外验证 API `/api/v1`
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /verify | 验证权限 `{user_id, type, target_name}` → `{allowed}` |
| GET | /users/{id}/tools | 用户可用工具列表 |
| GET | /users/{id}/skills | 用户可用技能列表 |

## 数据库表结构

| 表名 | 说明 | 核心字段 |
|------|------|---------|
| users | 用户表（飞书同步） | id, feishu_id, name, email, avatar, department_id, status, is_admin |
| departments | 部门表（飞书同步） | id, feishu_id, name, parent_id, path, status |
| roles | 角色表 | id, name, description |
| skills | 技能表 | id, name, description, config(JSON), status, created_by |
| tools | 工具表 | id, skill_id, name, description, parameters(JSON), endpoint, method, status, created_by |
| user_roles | 用户-角色关联 | id, user_id, role_id |
| role_skills | 角色-技能关联 | id, role_id, skill_id |
| role_tools | 角色-工具关联 | id, role_id, tool_id |
| permission_requests | 权限申请表 | id, user_id, type, target_id, reason, status, reviewed_by, review_comment |
| audit_logs | 审计日志 | id, user_id, action, target_type, target_id, detail, ip_address |

## 快速开始

### 前置条件

- Python 3.13+
- Node.js 20+
- MySQL 8.0+
- uv（Python 包管理器）
- Docker & docker-compose（可选，用于容器化部署）

### 本地开发

#### 1. 后端

```bash
# 安装依赖（uv workspace）
uv sync

# 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env 填入实际配置

# 创建数据库
mysql -u root -p -e "CREATE DATABASE toolhub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 执行数据库迁移
cd backend
alembic upgrade head

# 启动后端服务
uvicorn app.main:app --reload --port 8000
```

#### 2. 管理端前端

```bash
cd frontend/admin
npm install
npm run dev     # http://localhost:5174
```

#### 3. 客户端前端

```bash
cd frontend/client
npm install
npm run dev     # http://localhost:5173
```

### Docker 部署

```bash
# 配置环境变量
cp .env.example .env
# 编辑 .env 填入实际配置（飞书AppID/Secret、JWT密钥等）

# 一键启动
docker-compose up -d

# 服务地址：
#   客户端: http://localhost:80
#   管理端: http://localhost:81
#   后端API: http://localhost:8000
#   API文档: http://localhost:8000/docs
```

### 飞书应用配置

1. 在[飞书开放平台](https://open.feishu.cn/)创建企业自建应用
2. 开启 **网页应用** 能力，配置重定向 URL 为 `http://localhost:5173/auth/callback`
3. 添加 **通讯录** 权限（`contact:department.list`、`contact:user.id` 等）
4. 将 `App ID` 和 `App Secret` 填入 `.env` 配置

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | MySQL 连接字符串 | `mysql+pymysql://root:password@localhost:3306/toolhub` |
| `JWT_SECRET_KEY` | JWT 签名密钥 | 需修改为随机字符串 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token 有效期（分钟） | `1440`（24小时） |
| `FEISHU_APP_ID` | 飞书应用 App ID | - |
| `FEISHU_APP_SECRET` | 飞书应用 App Secret | - |
| `FEISHU_REDIRECT_URI` | 飞书回调地址 | `http://localhost:5173/auth/callback` |
| `CORS_ORIGINS` | 允许的跨域来源 | `["http://localhost:5173","http://localhost:5174"]` |
