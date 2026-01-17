# Dachuang-MS 系统模块划分与实现说明

本文基于仓库当前代码（Django + DRF 后端、Vue3 + Vite 前端）对系统进行模块化拆解，说明每个模块“做什么”和“怎么做”，并补充关键业务流程串联方式，便于小组汇报与交接。

## 1. 系统总体结构

- 后端：`backend/`（Django + DRF，API 前缀：`/api/v1`，JWT 鉴权：SimpleJWT）
- 前端：`frontend/`（Vue 3 + Vite + Pinia + Element Plus，统一 Axios 封装）
- 数据库：PostgreSQL（结构/数据：`dachuang_db_full.sql`，结构：`dachuang_db_schema.sql`）

后端路由入口：`backend/config/urls.py`  
前端路由入口：`frontend/src/router/index.ts`

## 2. 模块划分（大模块）

从业务与代码结构上，系统可以归纳为以下 7 个核心模块（后端为主，前端按角色页面映射对应业务）：

1) 用户与权限（含角色/管理员范围）  
2) 项目管理（含立项/中期/结题/成果/经费/异动/归档）  
3) 审核与评审（含专家组、任务分配、审核流转、统计）  
4) 系统配置与工作流（批次、配置项、工作流节点、管理员自动匹配）  
5) 数据字典（所有下拉选项、学院/项目类别/成果类型等）  
6) 通知中心（站内通知、未读统计、批量发送）  
7) 前端 UI（按学生/教师/管理员角色的页面与 API 调用封装）

下文按模块逐一说明。

---

## 3. 模块 1：用户与权限（`apps.users`）

### 3.1 工作内容（做什么）

- 登录与鉴权：基于学号/工号登录，签发 JWT（access/refresh）
- 用户资料：查看/修改个人资料、修改密码
- 用户管理：管理员对用户进行增删改查、禁用启用、重置密码、批量导入
- 角色管理：校级管理员可创建二级管理员角色（带“管理范围维度”），用于自动分配院系/范围管理员

### 3.2 关键实现（怎么做）

- 数据模型
  - `backend/apps/users/models.py`
    - `User`：扩展 `AbstractUser`，引入 `employee_id`（学号/工号）与 `role_fk`
    - `Role`：自定义角色表，字段 `scope_dimension` 用于“二级管理员数据范围维度”
- 鉴权与 Token
  - `backend/apps/users/views/public/auth.py`：`AuthViewSet.login/profile/update_profile/change_password`
  - `backend/apps/users/services/auth_service.py`：使用 `RefreshToken.for_user` 生成 JWT
  - `backend/config/settings.py`：`REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES` 指向 JWT
- 权限与角色判断
  - `backend/apps/users/permissions.py`：`IsLevel1Admin` / `IsAdmin`
  - `backend/apps/users/models.py`：`is_admin/is_level1_admin/is_student/is_teacher` 等属性集中封装
- 用户管理与导入
  - `backend/apps/users/views/admin/users.py`：管理员端用户列表、设置专家、禁用、重置等
  - `backend/apps/users/services/user_service.py`：业务逻辑（含 Excel 导入：`openpyxl/xlrd`）
- 角色管理
  - `backend/apps/users/views/role_views.py`：校级管理员创建/维护角色；创建的角色默认视为二级管理员（需 `scope_dimension`）

---

## 4. 模块 2：项目管理（`apps.projects`）

### 4.1 工作内容（做什么）

围绕“大创项目”生命周期提供全量能力：

- 项目基础信息：创建/编辑/列表/详情、成员与导师维护
- 立项申报：草稿/提交、材料上传、校验规则（人数上限、重复参与等）
- 中期检查：草稿/提交、材料上传、退回后重新提交（多轮次）
- 结题申请：草稿/提交、成果维护、结题材料、预期成果完成校验
- 成果管理：论文/专利/竞赛等成果记录、附件上传
- 经费管理：支出记录（余额校验）
- 项目异动：变更/延期/终止申请（独立审核链）
- 归档与导出：归档快照、批量导出 Excel/附件、证书/文档生成

### 4.2 关键实现（怎么做）

- 核心模型与生命周期状态
  - `backend/apps/projects/models.py`
    - `Project`：主表，`status` 覆盖立项/中期/结题等状态机
    - `ProjectPhaseInstance`：阶段实例（APPLICATION/MID_TERM/CLOSURE），支持退回后 `attempt_no` 自增
    - `ProjectAchievement` / `ProjectExpenditure` / `ProjectChangeRequest` / `ProjectArchive` 等子表
- 主 API 与 mixin 拆分
  - `backend/apps/projects/views/public/project.py`：`ProjectViewSet`，通过大量 mixin 聚合能力（减少单文件复杂度）
  - `backend/apps/projects/views/mixins/`：将“成员/成果/中期/结题/工作流/导出”等 endpoint 分离
- 立项/中期/结题入口（面向页面的专用 ViewSet）
  - `backend/apps/projects/views/public/application.py` + `backend/apps/projects/services/application_service.py`
  - `backend/apps/projects/views/mixins/project_midterm_mixin.py`
  - `backend/apps/projects/views/mixins/project_closure_mixin.py`
  - 典型逻辑：校验时间窗口（工作流节点日期）、写入项目状态、创建阶段实例、创建审核记录、发送通知
- 经费（余额校验）
  - `backend/apps/projects/views/public/expenditure.py`：创建支出前调用 `ProjectService.get_budget_stats` 做“剩余金额”校验
- 异动（独立审核链）
  - `backend/apps/projects/views/public/changes.py`
  - `backend/apps/projects/services/change_service.py`：TEACHER → LEVEL2 → LEVEL1 的顺序推进并最终生效
- 归档与导出
  - `backend/apps/projects/services/archive_service.py`：归档时保存项目快照（serializer 数据）与附件清单
  - `backend/apps/projects/views/mixins/project_admin_export_data_mixin.py`：Excel 导出（面向管理员）
  - `backend/apps/projects/views/mixins/project_admin_export_attachments_mixin.py`：批量打包附件
  - `backend/apps/projects/views/mixins/project_admin_export_certificates_mixin.py`：批量生成结题证书 HTML（zip）
  - `backend/apps/projects/services/document.py`：生成 docx（python-docx）

---

## 5. 模块 3：审核与评审（`apps.reviews`）

### 5.1 工作内容（做什么）

- 审核记录：导师审核、学院审核、校级审核的统一“审核记录”抽象
- 专家组：管理员创建专家组、维护成员
- 专家评审任务分配：将项目批量分配给某个专家组（生成“专家评审”审核记录）
- 审核流转：审核通过推进到下一节点；驳回退回到指定节点/默认节点
- 统计：管理员首页展示不同类型待审数量

### 5.2 关键实现（怎么做）

- 模型层
  - `backend/apps/reviews/models.py`
    - `Review`：审核记录，关联 `project` + `phase_instance` + `workflow_node`
    - `ExpertGroup`：专家组（`members` 为教师集合）
- API 层
  - `backend/apps/reviews/views/review.py`：`ReviewViewSet`（审核列表过滤、执行审核、退回目标查询）
  - `backend/apps/reviews/views/expert_groups.py`：`ExpertGroupViewSet`
  - `backend/apps/reviews/views/assignments.py`：`ReviewAssignmentViewSet.assign_batch`（批量分配专家任务）
  - `backend/apps/reviews/views/statistics.py`：`ReviewStatisticsViewSet.pending_counts`
- 核心业务逻辑（流转引擎）
  - `backend/apps/reviews/services/__init__.py`：`ReviewService`
    - `create_*_teacher_review`：在学生提交后创建导师审核
    - `approve_review/reject_review`：更新审核记录并驱动工作流推进/退回
    - `assign_project_to_group`：为专家组成员创建 `is_expert_review=True` 的评审任务
  - 与工作流节点联动：通过 `workflow_node_id` + `ProjectPhaseInstance.current_node_id` 绑定“当前节点”

---

## 6. 模块 4：系统配置与工作流（`apps.system_settings`）

### 6.1 工作内容（做什么）

- 批次（年度/批次）管理：支持设置当前批次，批次状态流转（草稿→进行中→结束→归档）
- 系统配置（JSON）：每个批次可配置 LIMIT/校验/时间窗口等
- 工作流配置：不同批次、不同阶段（立项/中期/结题）可配置不同审核节点序列
- 管理员自动匹配：二级管理员按“管理范围维度”自动匹配到负责该项目的管理员用户

### 6.2 关键实现（怎么做）

- 数据模型
  - `backend/apps/system_settings/models.py`
    - `ProjectBatch`：批次
    - `SystemSetting`：配置项（JSON），按 `code + batch` 唯一
    - `WorkflowConfig` / `WorkflowNode`：阶段工作流与节点（支持排序、退回规则、日期窗口、专家评审开关）
- 工作流服务（读取与校验）
  - `backend/apps/system_settings/services/workflow_service.py`
    - `get_active_workflow/get_nodes/get_node_by_id/get_next_node_by_id`
    - `check_phase_window/check_node_time_window`（按节点日期控制提交/审核窗口）
    - `validate_workflow_nodes`：校验节点合法性（学生节点位置、退回规则等）
- 批次工作流配置 API（校级管理员）
  - `backend/apps/system_settings/views/batch_workflow.py`：初始化默认工作流、增删改节点、节点重排、工作流汇总
- 管理员自动分配（关键联动点）
  - `backend/apps/system_settings/services/admin_assignment_service.py`
    - `resolve_admin_user`：根据 `workflow_node.role_fk.scope_dimension` + 项目维度值，定位唯一管理员
    - 维度值来自数据字典（如学院、项目类别、项目级别、重点领域）

---

## 7. 模块 5：数据字典（`apps.dictionaries`）

### 7.1 工作内容（做什么）

- 统一管理系统下拉选项与枚举：学院、项目类别、项目级别、成果类型、重点领域等
- 支持批量获取字典（前端初始化缓存）
- 支持批量导入/清空条目（校级管理员）

### 7.2 关键实现（怎么做）

- 模型
  - `backend/apps/dictionaries/models.py`：`DictionaryType` + `DictionaryItem`
  - 项目中的 `Project.level/category/source`、用户的 `managed_scope_value` 等均引用 `DictionaryItem`
- API
  - `backend/apps/dictionaries/views/__init__.py`
    - `DictionaryTypeViewSet.by_code/batch/all`：前端常用的批量拉取接口
    - `DictionaryItemViewSet.bulk/clear`：管理员批量维护
- 初始化数据
  - `backend/apps/dictionaries/migrations/`：通过迁移写入内置字典与初始条目

---

## 8. 模块 6：通知中心（`apps.notifications`）

### 8.1 工作内容（做什么）

- 站内通知列表（只读）、标记已读/全部已读、未读数量
- 管理员批量发送系统通知
- 业务触发通知：学生提交、导师/管理员审核结果、专家评审任务分配等

### 8.2 关键实现（怎么做）

- 模型与序列化
  - `backend/apps/notifications/models.py`：`Notification`
  - `backend/apps/notifications/serializers/__init__.py`：通知展示字段、关联项目标题
- API
  - `backend/apps/notifications/views/__init__.py`：`NotificationViewSet`
- 业务触发点（服务层）
  - `backend/apps/notifications/services/__init__.py`：`NotificationService`
  - 被调用位置示例：
    - 立项提交：`backend/apps/projects/views/mixins/project_core_actions_mixin.py`
    - 中期/结题提交：`backend/apps/projects/views/mixins/project_midterm_mixin.py`、`backend/apps/projects/views/mixins/project_closure_mixin.py`
    - 审核结果：`backend/apps/reviews/views/review.py`

---

## 9. 模块 7：前端 UI（`frontend/`）

### 9.1 工作内容（做什么）

- 按角色组织页面：学生（立项/中期/结题/经费/异动）、教师（待办/项目）、管理员（用户/项目/审核/配置/专家/统计）
- 统一 API 调用与错误处理：自动带 token、统一后端 `{code,message,data}` 格式
- 全局登录态管理：token、用户信息、角色信息（含后端角色扩展字段）

### 9.2 关键实现（怎么做）

- 路由与角色守卫
  - `frontend/src/router/index.ts`：路由注册 + `beforeEach`（未登录跳转、按角色跳转、meta.role 校验）
  - `frontend/src/router/modules/*Routes.ts`：按学生/教师/管理员拆分路由
- 状态管理
  - `frontend/src/stores/user.ts`：Pinia store，维护 token/user/roleInfo，并持久化到 `localStorage`
- 请求封装
  - `frontend/src/utils/request.ts`：Axios 实例 + 拦截器（自动注入 `Authorization: Bearer`，统一错误弹窗）
  - `frontend/src/api/**`：按后端模块划分的 API 封装（auth/projects/reviews/system-settings/dictionaries/users/notifications）
- 视图分区（与后端模块一一对应）
  - `frontend/src/views/student/**`
  - `frontend/src/views/teacher/**`
  - `frontend/src/views/admin/**`（level1/level2/shared）

---

## 10. 关键业务流程串联（从“模块”到“流程”）

### 10.1 登录与鉴权

1) 前端 `login()` → `POST /api/v1/auth/login/`（`backend/apps/users/views/public/auth.py`）  
2) 后端签发 JWT，返回 `access_token/refresh_token/user(role_info)`（`backend/apps/users/services/auth_service.py`）  
3) 前端把 token 写入 `localStorage`，路由守卫按 `user_role/roleInfo.default_route` 跳转（`frontend/src/stores/user.ts`、`frontend/src/router/index.ts`）

### 10.2 立项（APPLICATION）

1) 学生创建草稿/提交（`/api/v1/projects/application/create/`）  
2) 提交后创建导师审核 `Review` + 创建/更新 `ProjectPhaseInstance`（`ReviewService.create_teacher_review`、`ProjectPhaseService.ensure_current`）  
3) 审核通过/驳回由 `ReviewService.approve_review/reject_review` 驱动：
   - 通过：推进到下一 `WorkflowNode`，必要时自动创建下一条审核记录  
   - 驳回：按节点退回规则退回到目标节点，并标记阶段实例为 RETURNED（用于重新提交时开新轮次）

### 10.3 中期（MID_TERM）

1) 学生提交中期（`ProjectMidtermMixin.apply_mid_term/submit_mid_term`）  
2) 创建中期导师审核（`ReviewService.create_mid_term_teacher_review`）  
3) 审核流转逻辑与立项一致（工作流节点/阶段实例驱动）

### 10.4 结题（CLOSURE）

1) 学生提交结题（`ProjectClosureMixin.apply_closure/submit_closure`）  
2) 结题提交前校验：结题报告/至少 1 项成果/预期成果完成情况（`ProjectService.submit_closure`、`ProjectClosureService`）  
3) 审核通过到流程末尾时：项目状态置为 `CLOSED` 并触发归档（`ensure_project_archive`）

### 10.5 专家评审分配与进度汇总

- 管理员创建专家组（`ExpertGroupViewSet`）并批量分配项目给专家组（`ReviewAssignmentViewSet.assign_batch`）  
- 分配后为每位专家生成 `is_expert_review=True` 的 Review 任务（`ReviewService.assign_project_to_group`）  
- 管理员/页面可通过 `ProjectWorkflowMixin.expert_summary` 查看当前节点专家评审完成情况

### 10.6 项目异动（变更/延期/终止）

异动使用独立的 `ProjectChangeRequest/ProjectChangeReview` 审核链：  
学生创建草稿→提交→导师（可选）→院级→校级→最终对 `Project` 生效（`ProjectChangeService.apply_change`）。

---

## 11. 代码审阅要点（用于小组复盘）

以下为阅读代码时发现的“实现细节/潜在风险点”，建议在答辩或后续迭代中统一口径：

- 角色字段存在“新旧并存”：后端模型以 `role_fk` 为主，但部分逻辑仍依赖 `WorkflowNode.role` 或字符串角色；需要确保迁移数据完整（`WorkflowNode.get_role_code()` 已做兼容）。
- 通知批量发送接口里对用户角色的筛选使用了 `role` 字段：当前用户模型主要为 `role_fk`，这里可能触发 Django `FieldError`（`backend/apps/notifications/views/__init__.py`）。
- `BudgetService` 引用了未实现的通知方法（`notify_expenditure_*`），且与当前经费录入主流程（`ProjectExpenditureViewSet`）并不一致，建议确认是否“历史遗留/未接入”。
- 登出接口当前仅返回成功消息，未做 refresh token blacklisting（如需要更强安全，可补齐 `AuthService.handle_logout` 的调用链）。

> 注：以上不影响“模块划分与主要业务链路”的理解，但会影响线上稳定性与一致性，建议小组在最终交付前做一次统一收敛。

