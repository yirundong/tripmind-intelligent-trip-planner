# 4.1 系统架构实现

## 4.1.1 整体架构

本系统采用前后端分离的浏览器/服务器架构进行开发，整体由前端 Web 应用、后端服务、数据库与外部服务四个部分组成，各部分之间通过 HTTP 接口或数据库连接进行通信。系统总体架构如图 4-1 所示。

【图 4-1 系统总体架构图】

> 图 4-1 由 ARCHITECTURE.md "总体架构" Mermaid 图导出，可使用 mermaid-cli 或在线工具转成 PNG/SVG 后插入。

## 4.1.2 技术栈

系统在前端、后端、AI 编排、外部服务与导出五个层面分别选用了成熟的开源框架与开放服务，整体技术栈如表 4-1 所示。

**表 4-1  系统技术栈**

| 层级 | 技术 |
| --- | --- |
| 前端 | Vue 3、TypeScript、Vite、Ant Design Vue、Axios、AMap JS API |
| 后端 | FastAPI、Pydantic、SQLAlchemy、PostgreSQL、JWT |
| AI 编排 | LangGraph、LangChain、OpenAI 兼容模型接口 |
| 外部服务 | 高德地图 REST API、Unsplash 图片服务 |
| 导出 | html2canvas、jsPDF |

## 4.1.3 项目目录结构

整个项目按"前端、后端、文档、脚本"四类目录平级组织，每一类目录承担单一职责、互不依赖，便于团队协作与版本管理。项目整体的目录结构如图 4-2 所示。

【图 4-2 项目整体目录结构截图】

```text
intelligent-trip-planner/
├── backend/
│   ├── app/
│   │   ├── agents/              # LangGraph 多 Agent 工作流
│   │   ├── api/routes/          # FastAPI 路由
│   │   ├── models/              # Pydantic 请求/响应模型
│   │   ├── services/            # LLM、地图、图片服务封装
│   │   ├── tools/               # LangChain 工具
│   │   ├── auth.py              # JWT、密码哈希、当前用户
│   │   ├── database.py          # 数据库连接和 Session
│   │   └── db_models.py         # SQLAlchemy ORM 模型
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── services/            # API 请求封装
│   │   ├── styles/              # 全局样式
│   │   ├── types/               # TypeScript 类型
│   │   └── views/               # 页面视图
│   ├── package.json
│   └── .env.example
├── docs/
│   └── ARCHITECTURE.md          # 架构图、需求分析、实现说明与论文写作底稿
├── scripts/
│   └── init_postgres.sql        # PostgreSQL 建库和授权脚本
├── start-dev.ps1                # Windows 一键启动脚本
└── README.md
```

## 4.1.4 后端模块构成

后端将业务划分为多个独立模块，每个模块对应一个或多个源文件，承担单一职责并对外暴露明确的接口。后端模块构成如表 4-2 所示。

**表 4-2  后端模块构成**

| 模块 | 文件 | 作用 |
| --- | --- | --- |
| 应用入口 | `backend/app/api/main.py` | FastAPI 应用、CORS、路由挂载、启动事件 |
| 认证模块 | `backend/app/auth.py`、`backend/app/api/routes/auth.py` | 密码哈希、JWT、注册登录、个人资料 |
| 规划模块 | `backend/app/api/routes/trip.py` | 同步规划、异步任务创建、任务查询 |
| 行程收藏模块 | `backend/app/api/routes/trips.py` | Dashboard、行程增删改查、收藏增删改查 |
| 地图模块 | `backend/app/api/routes/map.py` | POI 搜索、天气查询、路线规划 |
| 图片模块 | `backend/app/api/routes/poi.py` | 景点图片查询 |
| 后台模块 | `backend/app/api/routes/admin.py` | 统计、任务日志、用户启停 |
| 智能体模块 | `backend/app/agents/trip_planner_agent.py` | LangGraph 多 Agent 工作流 |
| 服务封装 | `backend/app/services` | LLM、高德、Unsplash、管理员种子 |
| 数据库模块 | `backend/app/database.py`、`backend/app/db_models.py` | 数据库连接和 ORM 模型 |

## 4.1.5 前端模块构成

前端以页面为单位组织模块，每个模块对应一个或多个 .vue 单文件组件，承担一类完整的业务交互。前端模块构成如表 4-3 所示。

**表 4-3  前端模块构成**

| 模块 | 页面 | 作用 |
| --- | --- | --- |
| 认证模块 | 登录、注册、403 | 区分普通用户和管理员 |
| 工作台 | Dashboard | 展示行程、收藏、城市数量和最近行程 |
| 规划模块 | Home | 输入旅行需求，展示 Agent 运行进度 |
| 结果模块 | Result | 展示每日行程、地图、预算、天气和导出能力 |
| 行程模块 | MyTrips、TripDetail | 管理历史行程 |
| 收藏模块 | Favorites | 管理收藏地点 |
| 地图模块 | Explore、RoutePlanner | POI 探索和路线规划 |
| 用户画像 | Profile | 维护默认城市、交通、住宿和自定义标签 |
| 管理后台 | Admin | 查看用户、任务日志和系统统计，停用异常普通用户 |

## 4.1.6 主要前端页面

前端按业务划分为多个独立路由页面，每个页面对应一类完整的用户操作。系统主要前端页面如表 4-4 所示。

**表 4-4  主要前端页面**

| 页面 | 路径 | 说明 |
| --- | --- | --- |
| 登录 | `/login` | 普通用户和管理员统一登录入口 |
| 注册 | `/register` | 创建普通用户 |
| 工作台 | `/dashboard` | 用户行程、收藏和最近记录 |
| 规划 | `/` | 输入需求，创建异步 Agent 规划任务 |
| 结果 | `/result` | 展示每日行程、地图、预算和天气 |
| 我的行程 | `/trips` | 历史行程列表 |
| 收藏 | `/favorites` | 收藏地点管理 |
| 探索 | `/explore` | POI 搜索和地图标注 |
| 路线 | `/route-planner` | 两点路线规划 |
| 个人中心 | `/profile` | 默认城市、交通、住宿和自定义标签 |
| 管理后台 | `/admin` | 管理员统计、任务日志、用户列表 |

## 4.1.7 主要后端接口

系统对外通过 RESTful 风格的 HTTP 接口暴露能力，按业务划分为认证、行程规划、行程与收藏、地图、管理后台五类，主要接口如表 4-5 所示。

**表 4-5  主要后端接口**

| 接口 | 说明 |
| --- | --- |
| `POST /api/auth/register` | 注册 |
| `POST /api/auth/login` | 登录 |
| `GET /api/auth/me` | 当前用户信息 |
| `POST /api/trip/tasks` | 创建异步旅行规划任务 |
| `GET /api/trip/tasks/{task_id}` | 查询任务状态和进度 |
| `GET /api/trips` | 查询历史行程 |
| `GET /api/trips/{id}` | 查询行程详情 |
| `GET /api/favorites` | 查询收藏地点 |
| `GET /api/map/poi` | 高德 POI 搜索 |
| `POST /api/map/route` | 路线规划 |
| `GET /api/admin/stats` | 管理后台统计 |
| `GET /api/admin/tasks` | 管理后台任务日志 |
| `GET /api/admin/users` | 管理后台用户列表 |
| `PATCH /api/admin/users/{id}/active` | 启用或停用普通用户 |
