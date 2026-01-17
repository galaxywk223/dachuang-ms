# Dachuang-MS 四人分工说明（不含：系统配置与工作流 + 数据字典 + 项目立项流程 + 角色管理）

你已确定负责：

- 系统配置与工作流：批次、配置项、工作流节点、管理员自动匹配（`backend/apps/system_settings/`）
- 数据字典：下拉选项/学院/项目类别/成果类型等（`backend/apps/dictionaries/`）
- 项目立项流程：立项创建/修改/提交/撤回（立项阶段的学生侧流程与校验）
- 角色管理：角色列表、创建/更新/删除、启用/禁用（`/api/v1/auth/roles/…`）

你负责内容的实现落点（便于其他同学对接）：

- 角色管理：`backend/apps/users/views/role_views.py`（路由：`backend/apps/users/urls.py`）
  - `GET/POST/PUT/DELETE /api/v1/auth/roles/…`、`GET /api/v1/auth/roles/simple/`
- 立项流程（学生侧）：`backend/apps/projects/views/public/application.py`、`backend/apps/projects/services/application_service.py`
  - `POST /api/v1/projects/application/create/`、`PUT /api/v1/projects/application/{id}/update/`、`POST /api/v1/projects/application/{id}/withdraw/`
- 立项提交/回收站（触发导师审核）：`backend/apps/projects/views/mixins/project_core_actions_mixin.py`
  - `POST /api/v1/projects/{id}/submit/`、`POST /api/v1/projects/{id}/delete-application/`

下面把剩余工作按“业务域”均分给另外四位同学。每个人都需要覆盖：页面交互 + 接口调用 + 数据模型理解/校验（不做前后端拆分）。

---

## 成员 A：身份认证与用户体系（不含角色管理）

### 负责范围

- 登录鉴权、个人资料、修改密码
- 用户管理（管理员视角）：用户增删改查、启用/禁用、重置密码、批量导入
- 权限基建：一级管理员/通用管理员权限判断的统一口径

### 工作内容（做什么）

- 统一登录流程：学号/工号登录 → 获取 token 与用户信息（含 `role_info`）→ 保存登录态 → 退出清理
- 用户管理能力对齐业务：筛选（学院/角色/专家）、分页、导入模板校验、默认密码策略
- 角色相关信息展示/联动：读取并展示 `role_info`（但不改动角色定义与角色 CRUD）

### 实现落点（怎么做：关键文件）

- 后端接口与业务
  - 登录与资料：`backend/apps/users/views/public/auth.py`
  - 用户列表/管理：`backend/apps/users/views/public/users.py`、`backend/apps/users/views/admin/users.py`
  - 认证/用户服务：`backend/apps/users/services/auth_service.py`、`backend/apps/users/services/user_service.py`
  - 序列化与字段兼容：`backend/apps/users/serializers/__init__.py`
  - 权限类：`backend/apps/users/permissions.py`
- 路由入口
  - 后端：`backend/apps/users/urls.py`（挂载到 `backend/config/urls.py` 的 `/api/v1/auth/`）

### 关键接口（约定/核对）

- `POST /api/v1/auth/login/`
- `GET /api/v1/auth/profile/`、`PUT /api/v1/auth/profile/`
- `POST /api/v1/auth/change-password/`
- `GET/POST/PUT/DELETE /api/v1/auth/admin/users/…`

### 与你负责模块的对接点

- 用户的 `managed_scope_value` 会被“管理员自动匹配”用到：需要在“用户管理”里能正确配置/变更该字段（角色的 `scope_dimension` 由你在“角色管理”中维护）。

---

## 成员 B：项目流程（中期/结题）+ 项目管理基础能力

### 负责范围

- 中期/结题两大阶段的提交、退回、重提、多轮次（`ProjectPhaseInstance`）
- 项目管理基础能力：项目列表/详情、权限过滤、管理员修改项目基本信息与成员/导师
- 阶段时间窗口校验（按工作流节点日期窗口；你负责模块提供配置，他负责正确调用）

### 工作内容（做什么）

- 中期：草稿/提交、退回后再次提交时开新轮次（attempt）
- 结题：草稿/提交、提交前材料/成果校验、进入结题审核流转
- 项目基础信息维护：管理员侧修改项目、维护导师/成员；项目列表/详情按身份（学生/教师/管理员）正确可见
- 与审核模块（成员 D）对齐：审核通过/驳回后项目状态与阶段实例应一致

### 实现落点（怎么做：关键文件）

- 阶段实例与状态
  - 阶段实例模型：`backend/apps/projects/models.py`
  - 阶段实例服务：`backend/apps/projects/services/phase_service.py`
- 项目列表/详情与权限过滤
  - 项目资源：`backend/apps/projects/views/public/project.py`
  - 管理员项目维护：`backend/apps/projects/views/admin/project.py`
  - 成员增删：`backend/apps/projects/views/mixins/project_members_mixin.py`
- 中期/结题提交入口
  - 中期提交：`backend/apps/projects/views/mixins/project_midterm_mixin.py`
  - 结题提交：`backend/apps/projects/views/mixins/project_closure_mixin.py`

### 关键接口（约定/核对）

- 项目基础
  - `GET /api/v1/projects/…`、`GET /api/v1/projects/{id}/…`
  - `POST /api/v1/projects/{id}/add_member/`、`DELETE /api/v1/projects/{id}/remove-member/{member_id}/`
- 中期
  - `POST /api/v1/projects/{id}/apply-mid-term/`
  - `POST /api/v1/projects/{id}/submit-mid-term/`
  - `POST /api/v1/projects/{id}/delete-mid-term/`
- 结题
  - `POST /api/v1/projects/{id}/apply-closure/`
  - `POST /api/v1/projects/{id}/submit-closure/`
  - `POST /api/v1/projects/{id}/revoke-closure/`
  - `POST /api/v1/projects/{id}/delete-closure/`

### 与你负责模块的对接点

- 时间窗口校验来自工作流节点日期（你负责的工作流模块）：成员 B 只负责在“提交/审核入口”正确调用窗口检查并返回清晰提示。

---

## 成员 C：项目支撑能力（成果/经费/异动/归档与导出）

### 负责范围

- 成果管理、经费支出管理、项目异动（变更/延期/终止）
- 归档与导出：Excel、附件 zip、证书/文档生成、历史项目导入

### 工作内容（做什么）

- 成果：成果记录 CRUD 与附件、结题前成果校验支持
- 经费：支出录入权限与余额校验、支出列表查询
- 异动：申请、提交、审核链推进（与成员 D 的通知/待办对接）
- 归档导出：项目归档快照、批量导出数据/附件、证书预览与批量打包、docx 生成

### 实现落点（怎么做：关键文件）

- 成果/经费/异动
  - 成果：`backend/apps/projects/views/mixins/project_achievements_mixin.py`、`backend/apps/projects/views/public/achievement.py`
  - 经费：`backend/apps/projects/views/public/expenditure.py`
  - 异动：`backend/apps/projects/views/public/changes.py`、`backend/apps/projects/services/change_service.py`
- 归档与导出
  - 归档：`backend/apps/projects/services/archive_service.py`
  - 管理员导出：`backend/apps/projects/views/mixins/project_admin_export_data_mixin.py`
  - 附件打包：`backend/apps/projects/views/mixins/project_admin_export_attachments_mixin.py`
  - 证书：`backend/apps/projects/views/mixins/project_admin_export_certificates_mixin.py`、`backend/apps/projects/certificates.py`
  - 文档：`backend/apps/projects/services/document.py`、`backend/apps/projects/views/mixins/project_admin_export_documents_mixin.py`
  - 历史导入/批量操作：`backend/apps/projects/views/mixins/project_batch_mixin.py`

### 关键接口（约定/核对）

- 成果：`GET /api/v1/projects/{id}/achievements/`、`POST /api/v1/projects/{id}/add-achievement/`
- 经费：`/api/v1/projects/expenditures/…`（list/create/destroy），`GET /api/v1/projects/{id}/budget-stats/`
- 异动：`/api/v1/projects/change-requests/…` + `POST /api/v1/projects/change-requests/{id}/submit/` + `POST /api/v1/projects/change-requests/{id}/review/`
- 导出：`GET /api/v1/projects/admin/manage/export/`、`GET /api/v1/projects/admin/manage/batch-download/`、`GET /api/v1/projects/admin/manage/batch-certificates/`

### 与你负责模块的对接点

- 导出/证书/文档里会用到字典项（项目级别/学院等）的 label：需要你的“数据字典”稳定提供 `dict_type_code` 与条目 value/label。

---

## 成员 D：审核评审体系 + 通知中心 + 管理员待办统计

### 负责范围

- 审核记录的查询/执行审核/退回目标（含动态工作流节点）
- 专家组管理、评审任务分配（批量把项目分给专家组）
- 管理员待办统计（各类待审数量）
- 通知中心：通知列表、已读/未读、批量发送、业务触发通知的对齐

### 工作内容（做什么）

- 审核执行：统一校验（时间窗口、权限、评分规则），审核通过推进到下一节点，驳回按退回规则回退
- 专家评审：分配专家任务（生成 `is_expert_review=True` 的评审记录），保证“指导老师不参与本项目专家评审”等约束
- 待办统计：管理员首页各类待办数量汇总（立项/中期/结题/异动）
- 通知：提交/审核结果/专家任务分配时发送站内通知；通知中心支持未读统计与一键已读

### 实现落点（怎么做：关键文件）

- 审核与评审
  - 模型：`backend/apps/reviews/models.py`
  - 审核接口：`backend/apps/reviews/views/review.py`
  - 专家组：`backend/apps/reviews/views/expert_groups.py`
  - 分配任务：`backend/apps/reviews/views/assignments.py`
  - 审核逻辑：`backend/apps/reviews/services/__init__.py`（`approve_review/reject_review/assign_project_to_group/get_pending_reviews_for_admin`）
  - 待办统计：`backend/apps/reviews/views/statistics.py`
- 通知中心
  - 模型：`backend/apps/notifications/models.py`
  - 通知接口：`backend/apps/notifications/views/__init__.py`
  - 通知服务：`backend/apps/notifications/services/__init__.py`

### 关键接口（约定/核对）

- 审核：`/api/v1/reviews/…` + `POST /api/v1/reviews/{id}/review/` + `GET /api/v1/reviews/{id}/reject-targets/`
- 专家组：`/api/v1/reviews/groups/…`
- 分配：`POST /api/v1/reviews/assignments/assign_batch/`
- 待办统计：`GET /api/v1/reviews/statistics/pending-counts/`
- 通知：`/api/v1/notifications/…` + `POST /api/v1/notifications/{id}/mark_read/` + `GET /api/v1/notifications/unread_count/`

### 与你负责模块的对接点

- 审核推进/退回依赖“工作流节点配置”（你负责模块）：成员 D 需要保证 `workflow_node_id` 与 `ProjectPhaseInstance.current_node_id` 同步，退回目标使用你配置的 `allowed_reject_to`。

---

## 协作约定（建议写进组内共识）

- 字典与工作流由你统一维护“数据口径”：条目 value/label、节点 code/role_fk、时间窗口字段命名等保持稳定。
- 立项流程与角色管理由你统一维护：其他成员如需调整规则/字段/接口，先在组内对齐再改，避免影响全局联调。
- 其他四人修改涉及你的模块时，只通过接口与既定字段对接，不直接“硬编码字典值/节点序列”。
- 每个业务域的接口变更需同步更新：接口封装（`frontend/src/api/**`）、页面、以及对应的服务/视图调用链，避免“只改一侧”的联调成本。
