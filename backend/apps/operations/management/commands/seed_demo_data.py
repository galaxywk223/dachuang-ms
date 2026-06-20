import os
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.dictionaries.models import DictionaryItem, DictionaryType
from apps.notifications.models import PlatformMaterial, PlatformNotice
from apps.projects.models import Project, ProjectPhaseInstance
from apps.system_settings.models import ProjectBatch, WorkflowConfig, WorkflowNode
from apps.users.models import Role


User = get_user_model()

DEMO_PASSWORD_ENV = "DEMO_USER_PASSWORD"
DEMO_LEVEL1_USER_ENV = "DACHUANG_LEVEL1_USER"
DEMO_LEVEL2_USER_ENV = "DACHUANG_LEVEL2_USER"
DEMO_TEACHER_USER_ENV = "DACHUANG_TEACHER_USER"
DEMO_STUDENT_USER_ENV = "DACHUANG_STUDENT_USER"
WEAK_DEMO_PASSWORDS = {"123456", "admin123456", "password", "password123"}


class Command(BaseCommand):
    help = "Seed local demonstration data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            dest="password",
            default=os.environ.get(DEMO_PASSWORD_ENV),
            help="Password for local demo users.",
        )
        parser.add_argument("--level1-user", default=os.environ.get(DEMO_LEVEL1_USER_ENV))
        parser.add_argument("--level2-user", default=os.environ.get(DEMO_LEVEL2_USER_ENV))
        parser.add_argument("--teacher-user", default=os.environ.get(DEMO_TEACHER_USER_ENV))
        parser.add_argument("--student-user", default=os.environ.get(DEMO_STUDENT_USER_ENV))

    def handle(self, *args, **options):
        demo_password = self._demo_password(options.get("password"))
        demo_users = self._demo_users(options)
        roles = {
            "STUDENT": self._role("STUDENT", "学生"),
            "TEACHER": self._role("TEACHER", "指导教师"),
            "LEVEL2_ADMIN": self._role("LEVEL2_ADMIN", "院级管理员", "COLLEGE"),
            "LEVEL1_ADMIN": self._role("LEVEL1_ADMIN", "校级管理员", "SCHOOL"),
        }
        level = self._dictionary_item("project_level", "项目级别", "SCHOOL", "校级")
        category = self._dictionary_item("project_type", "项目类别", "INNOVATION", "创新训练")
        source = self._dictionary_item("project_source", "项目来源", "STUDENT", "学生自主选题")

        batch, _ = ProjectBatch.objects.update_or_create(
            code="DEMO2026",
            defaults={
                "name": "2026 年大创演示批次",
                "year": 2026,
                "status": ProjectBatch.STATUS_ACTIVE,
                "is_current": True,
                "is_active": True,
                "is_deleted": False,
            },
        )
        ProjectBatch.objects.exclude(id=batch.id).filter(is_current=True).update(
            is_current=False
        )

        student = self._user(
            "demo_student",
            demo_users["student"],
            "演示学生",
            roles["STUDENT"],
            demo_password,
            college="计算机学院",
            major="软件工程",
            grade="2026",
            class_name="软工1班",
        )
        self._user(
            "demo_teacher",
            demo_users["teacher"],
            "演示导师",
            roles["TEACHER"],
            demo_password,
            college="计算机学院",
            title="讲师",
        )
        self._user(
            "demo_level2",
            demo_users["level2"],
            "演示院级管理员",
            roles["LEVEL2_ADMIN"],
            demo_password,
            college="计算机学院",
        )
        admin = self._user(
            "demo_level1",
            demo_users["level1"],
            "演示校级管理员",
            roles["LEVEL1_ADMIN"],
            demo_password,
            college="创新创业学院",
        )

        students = [
            student,
            self._user(
                "demo_student_ai",
                self._derived_user_id(demo_users["student"], "A"),
                "陈启明",
                roles["STUDENT"],
                demo_password,
                college="计算机学院",
                major="人工智能",
                grade="2026",
                class_name="智能1班",
            ),
            self._user(
                "demo_student_iot",
                self._derived_user_id(demo_users["student"], "B"),
                "李思源",
                roles["STUDENT"],
                demo_password,
                college="电子信息学院",
                major="物联网工程",
                grade="2026",
                class_name="物联2班",
            ),
            self._user(
                "demo_student_design",
                self._derived_user_id(demo_users["student"], "C"),
                "周雨晴",
                roles["STUDENT"],
                demo_password,
                college="设计学院",
                major="数字媒体技术",
                grade="2026",
                class_name="数媒1班",
            ),
        ]

        projects = [
            self._project(
                project_no="DEMO20260001",
                title="智能校园大创管理平台演示项目",
                leader=students[0],
                batch=batch,
                source=source,
                level=level,
                category=category,
                admin=admin,
                rank=1,
                budget="3000.00",
                approved_budget="2800.00",
                status=Project.ProjectStatus.IN_PROGRESS,
                description="用于展示立项发布、任务中心和驾驶舱能力。",
                expected_results="系统原型、演示报告、答辩视频。",
            )
        ]
        visual_specs = [
            ("DEMO20260002", "AI 驱动的实验室安全巡检系统", students[1], 2, "5000.00", "4500.00", Project.ProjectStatus.IN_PROGRESS),
            ("DEMO20260003", "面向双碳校园的能耗预测平台", students[2], 3, "4200.00", "4000.00", Project.ProjectStatus.TEACHER_APPROVED),
            ("DEMO20260004", "多模态课堂专注度分析工具", students[1], 4, "3800.00", "3500.00", Project.ProjectStatus.COLLEGE_AUDITING),
            ("DEMO20260005", "高校科研成果智能推荐引擎", students[0], 5, "4600.00", "4200.00", Project.ProjectStatus.LEVEL1_AUDITING),
            ("DEMO20260006", "乡村振兴文旅数据可视化平台", students[3], 6, "3200.00", "3000.00", Project.ProjectStatus.READY_FOR_CLOSURE),
            ("DEMO20260007", "基于知识图谱的竞赛组队助手", students[2], 7, "3600.00", "3200.00", Project.ProjectStatus.MID_TERM_REVIEWING),
            ("DEMO20260008", "校园无障碍导航小程序", students[3], 8, "2800.00", "2600.00", Project.ProjectStatus.COMPLETED),
            ("DEMO20260009", "智慧教室设备健康监测系统", students[2], 9, "4100.00", "3900.00", Project.ProjectStatus.IN_PROGRESS),
            ("DEMO20260010", "低代码问卷与访谈分析平台", students[0], 10, "3000.00", "2800.00", Project.ProjectStatus.TEACHER_AUDITING),
            ("DEMO20260011", "心理健康咨询资源匹配系统", students[1], 11, "3400.00", "3100.00", Project.ProjectStatus.APPLICATION_RETURNED),
            ("DEMO20260012", "学生创新画像与成长档案系统", students[3], 12, "5200.00", "4800.00", Project.ProjectStatus.CLOSURE_LEVEL2_REVIEWING),
        ]
        for project_no, title, leader, rank, budget, approved_budget, status in visual_specs:
            projects.append(
                self._project(
                    project_no=project_no,
                    title=title,
                    leader=leader,
                    batch=batch,
                    source=source,
                    level=level,
                    category=category,
                    admin=admin,
                    rank=rank,
                    budget=budget,
                    approved_budget=approved_budget,
                    status=status,
                    description=f"{title}演示数据，用于统计图表、推荐排序与流程状态展示。",
                    expected_results="原型系统、研究报告、阶段汇报材料。",
                )
            )

        workflows = self._workflow_configs(batch, roles, admin)
        self._phase_instances(projects, workflows, admin)

        project = projects[0]

        PlatformNotice.objects.update_or_create(
            title="2026 年大创项目立项结果公示",
            defaults={
                "content": f"项目《{project.title}》已完成立项发布。",
                "target_roles": [],
                "status": PlatformNotice.NoticeStatus.PUBLISHED,
                "is_pinned": True,
                "published_at": timezone.now(),
                "created_by": admin,
            },
        )
        PlatformMaterial.objects.update_or_create(
            title="大创项目申报与结题材料模板",
            defaults={
                "description": "演示资料下载入口，可替换为正式模板文件或外部链接。",
                "category": "模板材料",
                "target_roles": [],
                "external_url": "https://example.com/demo-material",
                "is_active": True,
                "created_by": admin,
            },
        )

        self.stdout.write(self.style.SUCCESS("Local demo data seeded."))

    def _project(
        self,
        project_no,
        title,
        leader,
        batch,
        source,
        level,
        category,
        admin,
        rank,
        budget,
        approved_budget,
        status,
        description,
        expected_results,
    ):
        publish_status = (
            Project.PublishStatus.PUBLISHED
            if status in {
                Project.ProjectStatus.IN_PROGRESS,
                Project.ProjectStatus.MID_TERM_REVIEWING,
                Project.ProjectStatus.READY_FOR_CLOSURE,
                Project.ProjectStatus.CLOSURE_LEVEL2_REVIEWING,
                Project.ProjectStatus.COMPLETED,
            }
            else Project.PublishStatus.CONFIRMED
        )
        project, _ = Project.objects.update_or_create(
            project_no=project_no,
            defaults={
                "title": title,
                "leader": leader,
                "batch": batch,
                "year": batch.year,
                "source": source,
                "level": level,
                "category": category,
                "budget": Decimal(budget),
                "approved_budget": Decimal(approved_budget),
                "recommendation_rank": rank,
                "recommended_level": level,
                "recommended_budget": Decimal(approved_budget),
                "recommendation_comment": "学院综合评审后推荐进入校级立项池",
                "final_level": level,
                "final_budget": Decimal(approved_budget),
                "status": status,
                "publish_status": publish_status,
                "published_by": admin,
                "published_at": timezone.now(),
                "description": description,
                "expected_results": expected_results,
                "is_deleted": False,
            },
        )
        return project

    def _workflow_configs(self, batch, roles, admin):
        definitions = [
            (
                WorkflowConfig.Phase.APPLICATION,
                "立项申报多级审核流程",
                [
                    ("submit", "学生提交申报书", WorkflowNode.NodeType.SUBMIT, "STUDENT", False, WorkflowNode.ReturnPolicy.NONE),
                    ("teacher", "指导教师审核", WorkflowNode.NodeType.REVIEW, "TEACHER", False, WorkflowNode.ReturnPolicy.STUDENT),
                    ("college", "学院管理员初审与推荐", WorkflowNode.NodeType.REVIEW, "LEVEL2_ADMIN", True, WorkflowNode.ReturnPolicy.TEACHER),
                    ("school", "学校管理员终审确认", WorkflowNode.NodeType.APPROVAL, "LEVEL1_ADMIN", True, WorkflowNode.ReturnPolicy.PREVIOUS),
                    ("publish", "立项结果发布", WorkflowNode.NodeType.APPROVAL, "LEVEL1_ADMIN", False, WorkflowNode.ReturnPolicy.NONE),
                ],
            ),
            (
                WorkflowConfig.Phase.MID_TERM,
                "中期检查协同审核流程",
                [
                    ("mid_submit", "学生提交中期材料", WorkflowNode.NodeType.SUBMIT, "STUDENT", False, WorkflowNode.ReturnPolicy.NONE),
                    ("mid_teacher", "导师过程评价", WorkflowNode.NodeType.REVIEW, "TEACHER", False, WorkflowNode.ReturnPolicy.STUDENT),
                    ("mid_college", "学院中期审核", WorkflowNode.NodeType.REVIEW, "LEVEL2_ADMIN", True, WorkflowNode.ReturnPolicy.PREVIOUS),
                    ("mid_school", "学校抽检归档", WorkflowNode.NodeType.APPROVAL, "LEVEL1_ADMIN", False, WorkflowNode.ReturnPolicy.PREVIOUS),
                ],
            ),
            (
                WorkflowConfig.Phase.CLOSURE,
                "结题验收与成果归档流程",
                [
                    ("close_submit", "学生提交结题材料", WorkflowNode.NodeType.SUBMIT, "STUDENT", False, WorkflowNode.ReturnPolicy.NONE),
                    ("close_teacher", "导师验收意见", WorkflowNode.NodeType.REVIEW, "TEACHER", False, WorkflowNode.ReturnPolicy.STUDENT),
                    ("close_expert", "专家组成果评审", WorkflowNode.NodeType.REVIEW, "LEVEL2_ADMIN", True, WorkflowNode.ReturnPolicy.PREVIOUS),
                    ("close_school", "学校结题确认", WorkflowNode.NodeType.APPROVAL, "LEVEL1_ADMIN", True, WorkflowNode.ReturnPolicy.PREVIOUS),
                    ("archive", "证书与档案归集", WorkflowNode.NodeType.APPROVAL, "LEVEL1_ADMIN", False, WorkflowNode.ReturnPolicy.NONE),
                ],
            ),
            (
                WorkflowConfig.Phase.BUDGET,
                "经费支出分级审批流程",
                [
                    ("fund_submit", "负责人提交支出", WorkflowNode.NodeType.SUBMIT, "STUDENT", False, WorkflowNode.ReturnPolicy.NONE),
                    ("fund_teacher", "导师确认真实性", WorkflowNode.NodeType.REVIEW, "TEACHER", False, WorkflowNode.ReturnPolicy.STUDENT),
                    ("fund_college", "学院经费审核", WorkflowNode.NodeType.REVIEW, "LEVEL2_ADMIN", False, WorkflowNode.ReturnPolicy.PREVIOUS),
                    ("fund_school", "学校财务复核", WorkflowNode.NodeType.APPROVAL, "LEVEL1_ADMIN", False, WorkflowNode.ReturnPolicy.PREVIOUS),
                ],
            ),
            (
                WorkflowConfig.Phase.CHANGE,
                "项目异动申请审批流程",
                [
                    ("change_submit", "学生提交异动申请", WorkflowNode.NodeType.SUBMIT, "STUDENT", False, WorkflowNode.ReturnPolicy.NONE),
                    ("change_teacher", "导师审核变更原因", WorkflowNode.NodeType.REVIEW, "TEACHER", False, WorkflowNode.ReturnPolicy.STUDENT),
                    ("change_college", "学院管理员复核", WorkflowNode.NodeType.REVIEW, "LEVEL2_ADMIN", False, WorkflowNode.ReturnPolicy.PREVIOUS),
                    ("change_school", "学校管理员审批", WorkflowNode.NodeType.APPROVAL, "LEVEL1_ADMIN", False, WorkflowNode.ReturnPolicy.PREVIOUS),
                ],
            ),
        ]
        workflows = {}
        for phase, name, nodes in definitions:
            workflow, _ = WorkflowConfig.objects.update_or_create(
                phase=phase,
                batch=batch,
                version=1,
                defaults={
                    "name": name,
                    "description": "演示用真实工作流配置，覆盖提交、审核、专家评审、发布/归档等节点。",
                    "is_active": True,
                    "is_locked": False,
                    "created_by": admin,
                    "updated_by": admin,
                },
            )
            workflows[phase] = workflow
            previous = None
            for order, (code, node_name, node_type, role_code, expert, return_policy) in enumerate(nodes, start=1):
                node, _ = WorkflowNode.objects.update_or_create(
                    workflow=workflow,
                    code=code,
                    defaults={
                        "name": node_name,
                        "node_type": node_type,
                        "role_fk": roles[role_code],
                        "require_expert_review": expert,
                        "return_policy": return_policy,
                        "allowed_reject_to": previous.id if previous and return_policy != WorkflowNode.ReturnPolicy.NONE else None,
                        "notice": "请结合材料完整性、预算合理性与成果可交付性进行审核。",
                        "sort_order": order,
                        "is_active": True,
                    },
                )
                previous = node
        return workflows

    def _phase_instances(self, projects, workflows, admin):
        phase_map = [
            (WorkflowConfig.Phase.APPLICATION, ProjectPhaseInstance.Phase.APPLICATION),
            (WorkflowConfig.Phase.MID_TERM, ProjectPhaseInstance.Phase.MID_TERM),
            (WorkflowConfig.Phase.CLOSURE, ProjectPhaseInstance.Phase.CLOSURE),
        ]
        for index, project in enumerate(projects):
            for workflow_phase, instance_phase in phase_map:
                nodes = list(workflows[workflow_phase].nodes.all())
                if not nodes:
                    continue
                node = nodes[min(index % len(nodes), len(nodes) - 1)]
                state = ProjectPhaseInstance.State.COMPLETED if index % 4 == 0 else ProjectPhaseInstance.State.IN_PROGRESS
                if project.status == Project.ProjectStatus.APPLICATION_RETURNED:
                    state = ProjectPhaseInstance.State.RETURNED
                ProjectPhaseInstance.objects.update_or_create(
                    project=project,
                    phase=instance_phase,
                    attempt_no=1,
                    defaults={
                        "step": node.name,
                        "current_node_id": node.id,
                        "state": state,
                        "return_to": ProjectPhaseInstance.ReturnTo.STUDENT if state == ProjectPhaseInstance.State.RETURNED else "",
                        "returned_reason": "材料中的预算测算依据需要补充说明" if state == ProjectPhaseInstance.State.RETURNED else "",
                        "returned_at": timezone.now() if state == ProjectPhaseInstance.State.RETURNED else None,
                        "created_by": admin,
                    },
                )

    def _role(self, code, name, scope_dimension=None):
        role, _ = Role.objects.update_or_create(
            code=code,
            defaults={
                "name": name,
                "scope_dimension": scope_dimension,
                "is_active": True,
                "is_system": True,
            },
        )
        return role

    def _dictionary_item(self, type_code, type_name, value, label):
        dict_type, _ = DictionaryType.objects.get_or_create(
            code=type_code,
            defaults={"name": type_name, "is_system": True, "is_active": True},
        )
        item, _ = DictionaryItem.objects.update_or_create(
            dict_type=dict_type,
            value=value,
            defaults={"label": label, "is_active": True},
        )
        return item

    def _demo_password(self, configured_password):
        password = configured_password
        if not password:
            raise CommandError(
                f"{DEMO_PASSWORD_ENV} or --password must be configured."
            )
        if password in WEAK_DEMO_PASSWORDS or len(password) < 12:
            raise CommandError(
                "Demo user password must not use a weak shared value."
            )
        return password

    def _demo_users(self, options):
        values = {
            "level1": options.get("level1_user"),
            "level2": options.get("level2_user"),
            "teacher": options.get("teacher_user"),
            "student": options.get("student_user"),
        }
        missing = [key for key, value in values.items() if not value]
        if missing:
            raise CommandError(
                "Local demo user identifiers must be configured for: "
                + ", ".join(missing)
            )
        if len(set(values.values())) != len(values):
            raise CommandError("Local demo user identifiers must be unique.")
        return values

    def _derived_user_id(self, base_user_id, suffix):
        return f"{base_user_id}_{suffix}"

    def _user(self, username, employee_id, real_name, role, password, **extra):
        user, created = User.objects.update_or_create(
            employee_id=employee_id,
            defaults={
                "username": username,
                "real_name": real_name,
                "role_fk": role,
                "is_active": True,
                **extra,
            },
        )
        user.set_password(password)
        user.save(update_fields=["password"])
        return user
