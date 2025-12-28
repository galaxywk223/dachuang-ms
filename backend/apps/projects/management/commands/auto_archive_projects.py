"""
Auto archive closed projects and export an archive list.
"""

import csv
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.projects.models import Project, ProjectArchive
from apps.projects.services.archive_service import archive_projects


class Command(BaseCommand):
    help = "Auto archive closed projects and export an archive list."

    def add_arguments(self, parser):
        parser.add_argument("--batch-id", type=int, default=None, help="Filter by batch id.")
        parser.add_argument(
            "--before-days",
            type=int,
            default=None,
            help="Only archive projects updated before N days ago.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only show how many projects would be archived.",
        )
        parser.add_argument(
            "--no-export",
            action="store_true",
            help="Skip exporting archive list.",
        )
        parser.add_argument(
            "--export-dir",
            default=str(Path(settings.BASE_DIR) / "var" / "archives"),
            help="Directory to write archive list CSV.",
        )
        parser.add_argument(
            "--include-existing",
            action="store_true",
            help="Export all archive records instead of only new ones.",
        )

    def handle(self, *args, **options):
        qs = Project.objects.filter(status=Project.ProjectStatus.CLOSED)
        if options["batch_id"]:
            qs = qs.filter(batch_id=options["batch_id"])
        if options["before_days"] is not None:
            cutoff = timezone.now() - timedelta(days=options["before_days"])
            qs = qs.filter(updated_at__lte=cutoff)

        pending_qs = qs.filter(archive__isnull=True)
        pending_count = pending_qs.count()
        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS(f"Pending archives: {pending_count}"))
            return

        created_archives = archive_projects(pending_qs)
        created_count = len(created_archives)
        self.stdout.write(self.style.SUCCESS(f"Archived {created_count} projects."))

        if options["no_export"]:
            return

        export_dir = Path(options["export_dir"]).expanduser()
        export_dir.mkdir(parents=True, exist_ok=True)
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        export_path = export_dir / f"archive_list_{timestamp}.csv"

        if options["include_existing"]:
            archive_qs = ProjectArchive.objects.select_related(
                "project", "project__batch", "project__leader"
            ).order_by("-archived_at")
        else:
            ids = [archive.id for archive in created_archives]
            archive_qs = ProjectArchive.objects.filter(id__in=ids).select_related(
                "project", "project__batch", "project__leader"
            )

        self._export_csv(export_path, archive_qs)
        self.stdout.write(self.style.SUCCESS(f"Exported archive list: {export_path}"))

    @staticmethod
    def _export_csv(export_path, archive_qs):
        with export_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(
                [
                    "archived_at",
                    "project_no",
                    "title",
                    "leader_name",
                    "leader_id",
                    "batch_name",
                    "batch_year",
                    "status",
                ]
            )
            for archive in archive_qs:
                project = archive.project
                writer.writerow(
                    [
                        archive.archived_at.strftime("%Y-%m-%d %H:%M:%S"),
                        project.project_no,
                        project.title,
                        project.leader.real_name if project.leader else "",
                        project.leader.employee_id if project.leader else "",
                        project.batch.name if project.batch else "",
                        project.batch.year if project.batch else project.year,
                        project.status,
                    ]
                )
