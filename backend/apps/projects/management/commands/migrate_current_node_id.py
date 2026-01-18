"""
数据迁移命令：迁移现有项目的 current_node_id
优先使用 phase_instance.step 对应的节点，不再依赖项目状态推断
"""

from django.core.management.base import BaseCommand
from apps.projects.models import ProjectPhaseInstance
from apps.system_settings.services.workflow_service import WorkflowService


class Command(BaseCommand):
    help = "迁移现有项目的 current_node_id，根据项目状态反推流程节点"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="模拟运行，不实际更新数据库",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(self.style.WARNING("【模拟运行模式】不会实际更新数据"))

        # 获取所有ProjectPhaseInstance
        phase_instances = (
            ProjectPhaseInstance.objects.select_related("project", "project__batch")
            .filter(state=ProjectPhaseInstance.State.IN_PROGRESS)
            .order_by("project_id", "phase", "-attempt_no")
        )

        updated_count = 0
        skipped_count = 0
        error_count = 0

        for instance in phase_instances:
            try:
                project = instance.project
                phase = instance.phase

                # 获取该阶段的工作流节点
                nodes = WorkflowService.get_nodes(phase, project.batch)
                if not nodes:
                    self.stdout.write(
                        self.style.WARNING(
                            f"项目 {project.project_no} 阶段 {phase} 没有配置工作流节点，跳过"
                        )
                    )
                    skipped_count += 1
                    continue

                node = None
                if instance.step:
                    node = WorkflowService.get_node_by_code(
                        phase, instance.step, project.batch
                    )
                if not node:
                    node = WorkflowService.get_initial_node(phase, project.batch)
                current_node_id = None
                if node and WorkflowService.get_node_by_id(node.id):
                    current_node_id = node.id

                if current_node_id:
                    if not dry_run:
                        instance.current_node_id = current_node_id
                        instance.save(update_fields=["current_node_id"])

                    node = next((n for n in nodes if n.id == current_node_id), None)
                    node_name = node.name if node else f"ID:{current_node_id}"

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ 项目 {project.project_no} 阶段 {phase} -> 节点 {node_name}"
                        )
                    )
                    updated_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⊘ 项目 {project.project_no} 阶段 {phase} 无法推断当前节点"
                        )
                    )
                    skipped_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ 项目 {project.project_no} 处理失败: {str(e)}")
                )
                error_count += 1
                continue

        self.stdout.write(self.style.SUCCESS("\n迁移完成:"))
        self.stdout.write(f"  成功更新: {updated_count}")
        self.stdout.write(f"  跳过: {skipped_count}")
        self.stdout.write(f"  失败: {error_count}")

        if dry_run:
            self.stdout.write(self.style.WARNING("\n这是模拟运行，数据未实际更新"))
