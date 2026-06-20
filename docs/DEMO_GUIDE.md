# Dachuang-MS 演示与验收说明

## 脱敏演示数据

演示数据命令如下：

```powershell
cd backend
.\venv\Scripts\python.exe manage.py seed_demo_data --password "<strong-local-demo-password>"
```

演示用户标识通过本地环境变量提供：

```powershell
$env:DACHUANG_LEVEL1_USER="<local-level1-user-id>"
$env:DACHUANG_LEVEL2_USER="<local-level2-user-id>"
$env:DACHUANG_TEACHER_USER="<local-teacher-user-id>"
$env:DACHUANG_STUDENT_USER="<local-student-user-id>"
```

命令生成以下基础数据：

| 数据类型 | 内容 |
| --- | --- |
| 批次 | 脱敏演示批次 |
| 角色 | 学生、导师、院级管理员、校级管理员 |
| 项目 | 覆盖申报、审核、推荐、发布、过程管理和结题状态的演示项目 |
| 公告 | 立项结果公示公告 |
| 资料 | 申报与结题材料模板入口 |

演示数据仅用于本地功能验证和截图生成。公开仓库不提供任何登录凭据、线上服务地址或真实学院人员数据。

## 截图生成

自动截图脚本读取 `DACHUANG_DEMO_PASSWORD` 并传递给演示数据命令：

```powershell
$env:DACHUANG_DEMO_PASSWORD="<strong-local-demo-password>"
$env:DACHUANG_LEVEL1_USER="<local-level1-user-id>"
$env:DACHUANG_LEVEL2_USER="<local-level2-user-id>"
$env:DACHUANG_STUDENT_USER="<local-student-user-id>"
$env:DACHUANG_DEMO_PROJECT_NO="<local-demo-project-no>"
$env:DACHUANG_DEMO_BATCH_CODE="<local-demo-batch-code>"
node scripts/capture_screenshots.mjs
```

截图输出目录：

```text
docs/screenshots/
```

## 核心演示路径

| 步骤 | 角色 | 页面 | 演示结果 |
| --- | --- | --- | --- |
| 1 | 学生 | 我的项目 / 成果管理 | 项目立项后登记成果 |
| 2 | 院级管理员 | 项目推荐排序 | 维护推荐排序、推荐级别、推荐经费和推荐意见 |
| 3 | 校级管理员 | 立项发布中心 | 确认最终级别和经费，发布立项结果 |
| 4 | 校级管理员 | 任务中心 | 查看导入、导出任务和操作日志 |
| 5 | 校级管理员 | 数据中心 | 下载模板、上传文件、预校验、创建导入任务 |
| 6 | 校级管理员 | 统计概览 | 查看指标卡、阶段漏斗、学院对比、状态分布和风险视图 |
| 7 | 学生 | 通知公告 / 资料下载 | 查看公告和材料入口 |

## 截图清单

| 截图编号 | 页面 | 截图重点 |
| --- | --- | --- |
| 01 | 统计概览 | 可视化驾驶舱整体效果 |
| 02 | 项目推荐排序 | 学院推荐、排序和经费维护 |
| 03 | 立项发布中心 | 学校确认、结果发布和公告同步 |
| 04 | 项目详情 | 立项结果字段和流程时间线 |
| 05 | 数据中心 | 模板下载、预校验、任务回执 |
| 06 | 任务中心 | 后台任务和操作日志 |
| 07 | 学生端成果管理 | 成果登记入口 |
| 08 | 学生端通知公告 | 公告服务区 |
| 09 | 学生端资料下载 | 资料服务区 |

## 录屏路径

录屏建议按以下顺序组织：

1. 管理员登录后进入统计概览，展示系统首页。
2. 进入项目推荐排序，展示学院推荐和经费维护。
3. 进入立项发布中心，展示学校确认和结果发布。
4. 进入项目详情，展示最终级别、最终经费、发布状态和流程时间线。
5. 进入数据中心，展示模板下载、上传预校验和导入任务。
6. 进入任务中心，展示任务状态、结果下载和操作日志。
7. 切换学生端，展示成果管理、通知公告、资料下载。

## 验收命令

后端验证命令如下：

```powershell
cd backend
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py test
```

前端验证命令如下：

```powershell
cd frontend
npm run type-check
npm run build
```
