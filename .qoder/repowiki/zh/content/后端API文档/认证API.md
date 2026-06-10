# 认证API

<cite>
**本文引用的文件**
- [backend/app/api/auth.py](file://backend/app/api/auth.py)
- [backend/app/middleware/auth.py](file://backend/app/middleware/auth.py)
- [backend/app/services/auth.py](file://backend/app/services/auth.py)
- [backend/app/services/feishu.py](file://backend/app/services/feishu.py)
- [backend/app/utils/security.py](file://backend/app/utils/security.py)
- [backend/app/schemas/auth.py](file://backend/app/schemas/auth.py)
- [backend/app/models/user.py](file://backend/app/models/user.py)
- [backend/app/config.py](file://backend/app/config.py)
- [backend/app/main.py](file://backend/app/main.py)
- [frontend/client/src/pages/Login.tsx](file://frontend/client/src/pages/Login.tsx)
- [frontend/client/src/store/auth.ts](file://frontend/client/src/store/auth.ts)
- [frontend/client/src/api/request.ts](file://frontend/client/src/api/request.ts)
- [frontend/client/src/api/index.ts](file://frontend/client/src/api/index.ts)
</cite>

## 目录
1. [简介](#简介)
2. [项目结构](#项目结构)
3. [核心组件](#核心组件)
4. [架构总览](#架构总览)
5. [详细组件分析](#详细组件分析)
6. [依赖分析](#依赖分析)
7. [性能考虑](#性能考虑)
8. [故障排查指南](#故障排查指南)
9. [结论](#结论)
10. [附录](#附录)

## 简介
本文件为 ToolHub 的认证API文档，聚焦飞书OAuth2授权流程与JWT令牌管理。内容涵盖：
- 飞书OAuth2授权：授权链接生成、回调处理、用户信息获取与本地用户同步
- JWT令牌：生成、解码、校验与失效处理
- 认证中间件：请求拦截、令牌解析、权限校验（普通用户/管理员）
- 所有认证相关接口：登录、登出、获取当前用户信息
- 请求头设置、错误处理、安全注意事项
- 每个接口的请求示例与响应示例（以路径与字段形式给出）

## 项目结构
认证相关的核心模块分布于后端API层、服务层、中间件与工具层，并由前端负责发起授权与携带令牌访问受保护资源。

```mermaid
graph TB
subgraph "后端"
A["API 层<br/>/api/auth.py"]
B["认证中间件<br/>/middleware/auth.py"]
C["认证服务<br/>/services/auth.py"]
D["飞书服务<br/>/services/feishu.py"]
E["安全工具<br/>/utils/security.py"]
F["数据模型<br/>/models/user.py"]
G["配置<br/>/config.py"]
H["应用入口<br/>/main.py"]
end
subgraph "前端"
P1["登录页<br/>frontend/client/src/pages/Login.tsx"]
P2["全局请求拦截器<br/>frontend/client/src/api/request.ts"]
P3["API 封装<br/>frontend/client/src/api/index.ts"]
P4["状态存储<br/>frontend/client/src/store/auth.ts"]
end
P1 --> P3
P3 --> P2
P2 --> A
A --> C
C --> D
C --> E
C --> F
B --> E
B --> F
H --> A
H --> B
G --> D
G --> E
```

图表来源
- [backend/app/api/auth.py:1-48](file://backend/app/api/auth.py#L1-L48)
- [backend/app/middleware/auth.py:1-45](file://backend/app/middleware/auth.py#L1-L45)
- [backend/app/services/auth.py:1-80](file://backend/app/services/auth.py#L1-L80)
- [backend/app/services/feishu.py:1-120](file://backend/app/services/feishu.py#L1-L120)
- [backend/app/utils/security.py:1-32](file://backend/app/utils/security.py#L1-L32)
- [backend/app/models/user.py:1-116](file://backend/app/models/user.py#L1-L116)
- [backend/app/config.py:1-42](file://backend/app/config.py#L1-L42)
- [backend/app/main.py:1-61](file://backend/app/main.py#L1-L61)
- [frontend/client/src/pages/Login.tsx:1-52](file://frontend/client/src/pages/Login.tsx#L1-L52)
- [frontend/client/src/api/request.ts:1-28](file://frontend/client/src/api/request.ts#L1-L28)
- [frontend/client/src/api/index.ts:1-35](file://frontend/client/src/api/index.ts#L1-L35)
- [frontend/client/src/store/auth.ts:1-30](file://frontend/client/src/store/auth.ts#L1-L30)

章节来源
- [backend/app/main.py:25-42](file://backend/app/main.py#L25-L42)
- [backend/app/config.py:25-30](file://backend/app/config.py#L25-L30)

## 核心组件
- 授权路由与控制器：提供飞书登录、回调、登出、当前用户信息查询
- 认证服务：整合飞书授权码换token、拉取用户信息、本地用户创建/更新、JWT签发
- 飞书服务：封装飞书开放平台API（授权URL、tenant_access_token、用户access_token、用户信息）
- 安全工具：JWT生成与解码
- 认证中间件：基于Bearer Token的鉴权与权限控制
- 前端集成：发起授权、接收回调、持久化令牌、统一注入Authorization头

章节来源
- [backend/app/api/auth.py:13-47](file://backend/app/api/auth.py#L13-L47)
- [backend/app/services/auth.py:9-79](file://backend/app/services/auth.py#L9-L79)
- [backend/app/services/feishu.py:6-119](file://backend/app/services/feishu.py#L6-L119)
- [backend/app/utils/security.py:8-31](file://backend/app/utils/security.py#L8-L31)
- [backend/app/middleware/auth.py:12-44](file://backend/app/middleware/auth.py#L12-L44)
- [frontend/client/src/pages/Login.tsx:12-36](file://frontend/client/src/pages/Login.tsx#L12-L36)
- [frontend/client/src/api/request.ts:8-25](file://frontend/client/src/api/request.ts#L8-L25)

## 架构总览
下图展示从浏览器到后端认证链路的整体交互：

```mermaid
sequenceDiagram
participant Browser as "浏览器"
participant Front as "前端页面(Login.tsx)"
participant API as "后端认证API(auth.py)"
participant AuthSvc as "认证服务(auth.py)"
participant FSvc as "飞书服务(feishu.py)"
participant Sec as "安全工具(security.py)"
participant DB as "数据库(models/user.py)"
Browser->>Front : "点击飞书登录"
Front->>API : "GET /api/auth/feishu/login"
API->>AuthSvc : "获取飞书授权URL"
AuthSvc->>FSvc : "生成授权URL"
FSvc-->>API : "返回授权URL"
API-->>Front : "{ url }"
Browser->>Browser : "跳转至飞书授权页"
Browser->>API : "回调 GET /api/auth/feishu/callback?code=..."
API->>AuthSvc : "处理回调(code)"
AuthSvc->>FSvc : "换取用户access_token"
AuthSvc->>FSvc : "获取用户信息"
AuthSvc->>DB : "查找/创建/更新用户"
AuthSvc->>Sec : "生成JWT(access_token)"
Sec-->>AuthSvc : "JWT字符串"
AuthSvc-->>API : "TokenResponse"
API-->>Front : "{ access_token, user_id, name, is_admin }"
Browser->>API : "后续请求携带 Authorization : Bearer <token>"
API->>AuthSvc : "依赖中间件解析令牌"
AuthSvc->>Sec : "解码JWT"
Sec-->>AuthSvc : "TokenData(user_id,is_admin)"
AuthSvc->>DB : "按ID查询用户并校验状态"
DB-->>AuthSvc : "User对象"
AuthSvc-->>API : "current_user"
API-->>Browser : "业务响应"
```

图表来源
- [backend/app/api/auth.py:13-47](file://backend/app/api/auth.py#L13-L47)
- [backend/app/services/auth.py:16-76](file://backend/app/services/auth.py#L16-L76)
- [backend/app/services/feishu.py:15-69](file://backend/app/services/feishu.py#L15-L69)
- [backend/app/utils/security.py:20-31](file://backend/app/utils/security.py#L20-L31)
- [backend/app/middleware/auth.py:12-33](file://backend/app/middleware/auth.py#L12-L33)
- [frontend/client/src/pages/Login.tsx:12-36](file://frontend/client/src/pages/Login.tsx#L12-L36)
- [frontend/client/src/api/request.ts:8-14](file://frontend/client/src/api/request.ts#L8-L14)

## 详细组件分析

### 授权路由与控制器
- 路由前缀：/api/auth
- 主要接口
  - GET /feishu/login：生成飞书OAuth2授权URL
  - GET /feishu/callback：处理飞书回调，完成用户登录并发放JWT
  - POST /logout：登出（前端清理token即可）
  - GET /me：获取当前登录用户信息

请求与响应要点
- GET /feishu/login
  - 请求：无查询参数
  - 响应：包含url字段的对象
- GET /feishu/callback
  - 查询参数：code（必填）
  - 成功响应：TokenResponse对象
  - 失败响应：错误消息字符串
- POST /logout
  - 请求：无体
  - 响应：成功消息
- GET /me
  - 请求：需携带Authorization: Bearer <token>
  - 响应：当前用户基础信息集合

章节来源
- [backend/app/api/auth.py:13-47](file://backend/app/api/auth.py#L13-L47)
- [backend/app/schemas/auth.py:10-16](file://backend/app/schemas/auth.py#L10-L16)

### 认证服务（AuthService）
职责
- 生成飞书授权URL
- 处理回调：换取用户access_token、获取用户信息、查找/创建/更新本地用户、签发JWT
- 返回TokenResponse

关键流程
- 授权码换用户access_token
- 拉取用户信息（支持user_id或open_id）
- 用户同步：根据飞书ID查找本地用户；不存在则创建，存在则更新基本信息与部门映射
- JWT签发：包含user_id与is_admin

```mermaid
flowchart TD
Start(["进入 handle_feishu_callback"]) --> GetToken["换取用户access_token"]
GetToken --> GetUser["获取用户信息"]
GetUser --> FindUser{"本地是否存在该飞书用户？"}
FindUser --> |否| CreateUser["创建新用户并写入数据库"]
FindUser --> |是| UpdateUser["更新用户信息与部门映射"]
CreateUser --> GenJWT["生成JWT(access_token)"]
UpdateUser --> GenJWT
GenJWT --> Return["返回TokenResponse"]
```

图表来源
- [backend/app/services/auth.py:16-76](file://backend/app/services/auth.py#L16-L76)

章节来源
- [backend/app/services/auth.py:9-79](file://backend/app/services/auth.py#L9-L79)

### 飞书服务（FeishuService）
职责
- 生成飞书OAuth2授权URL
- 获取tenant_access_token（内部应用授权）
- 通过授权码换取用户access_token
- 获取飞书用户信息
- 提供部门列表/详情（扩展能力）

要点
- 使用配置中的FEISHU_APP_ID、FEISHU_APP_SECRET、FEISHU_REDIRECT_URI
- 内部获取tenant_access_token后用于后续调用
- 统一错误处理：当接口返回非成功码时抛出异常

章节来源
- [backend/app/services/feishu.py:6-119](file://backend/app/services/feishu.py#L6-L119)
- [backend/app/config.py:25-29](file://backend/app/config.py#L25-L29)

### 安全工具（JWT）
- 生成JWT：使用配置中的密钥与算法，设置过期时间
- 解码JWT：校验签名与过期，返回TokenData（包含user_id与is_admin）

章节来源
- [backend/app/utils/security.py:8-31](file://backend/app/utils/security.py#L8-L31)
- [backend/app/config.py:20-23](file://backend/app/config.py#L20-L23)

### 认证中间件（HTTP Bearer）
- 依赖HTTPBearer凭据，从Authorization头中提取Bearer token
- 解码JWT得到TokenData
- 数据库查询用户并校验状态为active
- 提供require_admin装饰器进行管理员权限校验

```mermaid
flowchart TD
Req["收到请求"] --> Extract["提取Authorization头"]
Extract --> Decode["decode_access_token(token)"]
Decode --> Valid{"解码成功且未过期？"}
Valid --> |否| Unauthorized["401 无效或过期令牌"]
Valid --> |是| LoadUser["按user_id查询用户"]
LoadUser --> Found{"用户存在且状态为active？"}
Found --> |否| Forbidden["401/403 用户不存在或未激活"]
Found --> |是| Next["放行，注入current_user"]
```

图表来源
- [backend/app/middleware/auth.py:12-33](file://backend/app/middleware/auth.py#L12-L33)
- [backend/app/utils/security.py:20-31](file://backend/app/utils/security.py#L20-L31)
- [backend/app/models/user.py:23-38](file://backend/app/models/user.py#L23-L38)

章节来源
- [backend/app/middleware/auth.py:12-44](file://backend/app/middleware/auth.py#L12-L44)

### 前端集成
- 登录页：调用后端获取飞书授权URL并跳转
- 回调处理：读取URL中的code，调用后端回调接口，保存access_token与用户信息
- 请求拦截：统一在请求头添加Authorization: Bearer <token>
- 登出：移除本地token并重定向到登录页

章节来源
- [frontend/client/src/pages/Login.tsx:12-36](file://frontend/client/src/pages/Login.tsx#L12-L36)
- [frontend/client/src/api/index.ts:3-8](file://frontend/client/src/api/index.ts#L3-L8)
- [frontend/client/src/api/request.ts:8-25](file://frontend/client/src/api/request.ts#L8-L25)
- [frontend/client/src/store/auth.ts:18-29](file://frontend/client/src/store/auth.ts#L18-L29)

## 依赖分析
- API层依赖认证服务与中间件
- 认证服务依赖飞书服务、安全工具与数据库模型
- 飞书服务依赖配置
- 中间件依赖安全工具与数据库模型
- 前端依赖API封装与请求拦截器

```mermaid
graph LR
API["auth.py"] --> Svc["services/auth.py"]
API --> MW["middleware/auth.py"]
Svc --> FS["services/feishu.py"]
Svc --> SEC["utils/security.py"]
Svc --> M["models/user.py"]
MW --> SEC
MW --> M
FS --> CFG["config.py"]
SEC --> CFG
MAIN["main.py"] --> API
MAIN --> MW
```

图表来源
- [backend/app/api/auth.py:1-8](file://backend/app/api/auth.py#L1-L8)
- [backend/app/services/auth.py:1-6](file://backend/app/services/auth.py#L1-L6)
- [backend/app/middleware/auth.py:1-7](file://backend/app/middleware/auth.py#L1-L7)
- [backend/app/services/feishu.py:1-4](file://backend/app/services/feishu.py#L1-L4)
- [backend/app/utils/security.py:1-5](file://backend/app/utils/security.py#L1-L5)
- [backend/app/models/user.py:1-4](file://backend/app/models/user.py#L1-L4)
- [backend/app/config.py:1-42](file://backend/app/config.py#L1-L42)
- [backend/app/main.py:1-61](file://backend/app/main.py#L1-L61)

章节来源
- [backend/app/main.py:25-42](file://backend/app/main.py#L25-L42)

## 性能考虑
- 飞书接口调用采用异步客户端，避免阻塞
- JWT生成/解码为纯内存计算，开销极低
- 用户查询按主键与索引字段进行，建议确保数据库索引健全
- 建议在生产环境启用更短的JWT过期时间并结合刷新策略（当前仓库未实现refresh接口）

## 故障排查指南
常见问题与定位
- 401 无效或过期令牌
  - 检查前端是否正确携带Authorization头
  - 检查JWT密钥、算法与过期时间配置
  - 检查中间件解码逻辑与用户状态
- 403 用户账户未激活
  - 检查用户状态字段是否为active
- 飞书回调失败
  - 检查FEISHU_APP_ID、FEISHU_APP_SECRET、FEISHU_REDIRECT_URI配置
  - 检查tenant_access_token获取与用户access_token换取流程
- 用户信息不同步
  - 检查飞书返回字段（user_id/open_id）与本地用户映射逻辑
  - 检查部门ID映射是否正确

章节来源
- [backend/app/middleware/auth.py:18-32](file://backend/app/middleware/auth.py#L18-L32)
- [backend/app/services/feishu.py:26-57](file://backend/app/services/feishu.py#L26-L57)
- [backend/app/services/auth.py:25-64](file://backend/app/services/auth.py#L25-L64)
- [backend/app/config.py:25-29](file://backend/app/config.py#L25-L29)

## 结论
本认证体系以飞书OAuth2为基础，结合JWT实现无状态会话管理。后端通过服务层整合外部API与本地用户模型，中间件统一处理鉴权与权限控制。前端通过拦截器自动注入令牌，简化了调用方实现。建议在生产环境中完善令牌刷新与更严格的错误处理与日志记录。

## 附录

### 接口定义与示例

- 获取飞书授权URL
  - 方法与路径：GET /api/auth/feishu/login
  - 请求头：无特殊要求
  - 查询参数：无
  - 成功响应字段：data.url
  - 示例请求
    - GET /api/auth/feishu/login
  - 示例响应
    - 200 OK
    - {
        "code": 0,
        "message": "success",
        "data": {
          "url": "https://open.feishu.cn/.../authorize?app_id=...&redirect_uri=...&response_type=code&state="
        }
      }

- 飞书回调
  - 方法与路径：GET /api/auth/feishu/callback
  - 请求头：无特殊要求
  - 查询参数：code（授权码）
  - 成功响应字段：access_token, token_type, user_id, name, is_admin
  - 示例请求
    - GET /api/auth/feishu/callback?code=xxx
  - 示例响应
    - 200 OK
    - {
        "code": 0,
        "message": "success",
        "data": {
          "access_token": "eyJhbGciOiJIUzI1NiIs...",
          "token_type": "bearer",
          "user_id": 123,
          "name": "张三",
          "is_admin": false
        }
      }

- 登出
  - 方法与路径：POST /api/auth/logout
  - 请求头：无特殊要求
  - 查询参数：无
  - 成功响应字段：message
  - 示例请求
    - POST /api/auth/logout
  - 示例响应
    - 200 OK
    - {
        "code": 0,
        "message": "success",
        "data": {
          "message": "Logged out successfully"
        }
      }

- 获取当前用户信息
  - 方法与路径：GET /api/auth/me
  - 请求头：Authorization: Bearer <access_token>
  - 查询参数：无
  - 成功响应字段：id, name, email, avatar, is_admin, status, department_id
  - 示例请求
    - GET /api/auth/me
    - Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
  - 示例响应
    - 200 OK
    - {
        "code": 0,
        "message": "success",
        "data": {
          "id": 123,
          "name": "张三",
          "email": "zhangsan@example.com",
          "avatar": "https://example.com/avatar.jpg",
          "is_admin": false,
          "status": "active",
          "department_id": 1
        }
      }

### 请求头设置
- 所有受保护接口均需携带Authorization头
  - Authorization: Bearer <access_token>
- 前端已通过拦截器自动注入

章节来源
- [frontend/client/src/api/request.ts:8-14](file://frontend/client/src/api/request.ts#L8-L14)
- [frontend/client/src/api/index.ts:3-8](file://frontend/client/src/api/index.ts#L3-L8)

### 错误处理
- 401 未授权
  - 无效或过期令牌
  - 用户不存在
- 403 禁止访问
  - 用户状态不为active
  - 需要管理员权限但当前用户非管理员
- 其他错误
  - 飞书接口调用失败时抛出异常，由上层捕获并返回错误响应

章节来源
- [backend/app/middleware/auth.py:18-32](file://backend/app/middleware/auth.py#L18-L32)
- [backend/app/api/auth.py:26](file://backend/app/api/auth.py#L26)

### 安全考虑
- 密钥与算法
  - 使用配置项JWT_SECRET_KEY、JWT_ALGORITHM
  - 建议在生产环境使用强密钥与HTTPS传输
- 过期时间
  - 默认24小时，建议按业务场景调整
- 回调地址
  - FEISHU_REDIRECT_URI需与飞书后台配置一致
- 前端存储
  - 令牌存储于localStorage，建议配合HttpOnly Cookie与安全存储方案（当前实现为前端本地存储）

章节来源
- [backend/app/config.py:20-29](file://backend/app/config.py#L20-L29)
- [frontend/client/src/store/auth.ts:18-29](file://frontend/client/src/store/auth.ts#L18-L29)