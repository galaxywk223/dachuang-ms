# 大创项目管理平台

面向高校创新创业项目管理的一体化解决方案，覆盖项目从立项申报、过程跟踪到结题归档的完整业务流程。系统分为 Django RESTful 后端与 Vue 3 单页前端，支持学生与多级管理员角色协作，提供灵活的权限控制与审核工作流。

- 🚀 **学生端**：在线提交立项、中期、结题资料，草稿与附件管理，进度实时查询。
- 🛠️ **管理员端**：多级审核、项目台账、用户与角色维护、流程状态追踪。
- 🔐 **统一认证**：基于 JWT 的登录态管理，支持角色切换与安全的接口访问。
- 📊 **可视化看板**：统计关键指标，辅助管理人员掌握项目运行态势。

---

## 技术栈

- **前端**：Vite · Vue 3 · TypeScript · Pinia · Vue Router · Element Plus
- **后端**：Python 3 · Django 4 · Django REST Framework · SimpleJWT · PostgreSQL
- **其他**：Sass、Axios、CORS、日志追踪

---

## 目录结构

```text
dachuang-ms/
├─ backend/                 # Django 后端服务
│  ├─ apps/                 # 业务模块（用户、项目、审核、通知等）
│  ├─ config/               # 全局配置与 URL 路由
│  ├─ logs/                 # 默认日志输出
│  ├─ manage.py
│  └─ requirements.txt
├─ frontend/                # Vue 单页应用
│  ├─ src/                  # 页面、组件、路由与状态管理
│  ├─ package.json
│  └─ vite.config.ts
├─ .vscode/                 # IDE 配置
└─ README.md
```

---

## 环境要求

- **Python** >= 3.10
- **Node.js** >= 18（推荐搭配 pnpm 或 npm 10）
- **PostgreSQL** >= 13
- **操作系统**：Windows / macOS / Linux

---

## 快速开始

### 1. 后端（Django + DRF）

```bash
cd backend
# 创建虚拟环境（可替换为你常用的管理方式）
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt

# 根据实际环境更新 config/settings.py 中的数据库与 SECRET_KEY
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

> 💡 默认数据库配置指向本地 PostgreSQL（库名 `dachuang_db`），如需个性化，请修改 `backend/config/settings.py` 或扩展为 `.env` 配置。

常用命令：

- `python manage.py makemigrations`：生成模型迁移
- `python manage.py migrate`：同步数据库
- `python manage.py shell`：调试脚本
- `python manage.py collectstatic`：生产环境静态资源收集

### 2. 前端（Vite + Vue 3）

```bash
cd frontend
npm install    # 或使用 pnpm / yarn

# 可在根目录创建 .env.development 自定义 API 地址
echo VITE_API_BASE_URL=http://localhost:8000 > .env.development

npm run dev    # 启动开发服务器，默认 http://localhost:5173
npm run build  # 构建产物
npm run preview
```

> 🔗 前端默认读取 `VITE_API_BASE_URL`，若未设置则 fallback 到 `http://localhost:8000`，请确保与后端服务端口一致。

---

## 功能模块概览

- **用户与权限**
  - 自定义用户模型，支持学生、二级管理员、一级管理员角色
  - JWT 登录注销、密码修改、资料维护与登录日志
  - 管理端可批量管理用户与角色分配
- **项目全流程管理**
  - 立项：申请、草稿箱、审核流（校级/院级）
  - 中期：提交材料、跟踪进度、审核反馈
  - 结题：成果归档、审批记录、文档管理
  - 多状态流转，项目成员信息与经费预算
- **审核与通知**
  - 多级审核视图（立项、中期、结题）
  - 业务通知模块，支持消息记录与提醒
- **仪表盘**
  - 管理端数据看板，展示项目数量、审批状态、角色占比等统计指标

---

## 部署与运维建议

- **生产环境**请务必：
  - 通过环境变量注入 `SECRET_KEY`、数据库凭据等敏感信息
  - 配置允许的域名 `ALLOWED_HOSTS` 与 CORS 白名单
  - 使用 `DEBUG = False` 并提供静态资源服务
  - 结合 `gunicorn/uvicorn + nginx`、`systemd` 等方案部署
- **数据库**建议开启定期备份，关键表可加上只读副本提升查询性能。
- **日志**默认输出至 `backend/logs/debug.log`，可根据需要扩展至集中式日志平台。

---

## 贡献指南

1. Fork 或创建特性分支
2. 遵循模块化目录结构，保持类型注释与接口文档更新
3. 提交前运行基础检查（例如 `npm run build`, `python manage.py test`）
4. 统一通过 Pull Request 讨论与合并

欢迎提交 Issue / PR 与我们共同完善系统。

---

## 许可证

本项目基于 [MIT License](LICENSE) 开源发布，详见许可证文件。

