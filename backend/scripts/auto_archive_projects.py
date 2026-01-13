#!/usr/bin/env python
"""
自动归档已结题项目脚本
用法: python manage.py shell < scripts/auto_archive_projects.py
或者: python scripts/auto_archive_projects.py
"""

import os
import sys
import django
from datetime import datetime, timedelta

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import transaction
from django.utils import timezone
from apps.projects.models import Project, ProjectArchive
from apps.projects.services.archive_service import ArchiveService


def auto_archive_projects(months_after_closure=6, dry_run=False):
    """
    自动归档已结题项目
    :param months_after_closure: 结题后多少个月进行归档（默认6个月）
    :param dry_run: 是否为试运行模式
    """
    print(f"{'[试运行]' if dry_run else '[执行]'} 开始自动归档项目...")
    print(f"归档条件：结题超过 {months_after_closure} 个月的项目\n")

    # 计算截止日期
    cutoff_date = timezone.now() - timedelta(days=months_after_closure * 30)

    # 查找符合条件的已结题项目
    projects_to_archive = Project.objects.filter(
        status=Project.ProjectStatus.CLOSED,
        is_deleted=False,
        updated_at__lt=cutoff_date,
    ).exclude(id__in=ProjectArchive.objects.values_list("project_id", flat=True))

    total_count = projects_to_archive.count()
    print(f"找到 {total_count} 个符合归档条件的项目\n")

    if total_count == 0:
        print("没有需要归档的项目")
        return

    success_count = 0
    failed_count = 0
    failed_list = []

    for project in projects_to_archive:
        try:
            print(f"处理项目: {project.project_no} - {project.title}")
            print(f"  结题时间: {project.updated_at}")
            print(f"  负责人: {project.leader.real_name if project.leader else '未知'}")

            if not dry_run:
                # 执行归档
                archive = ArchiveService.archive_project(project)
                print(f"  ✓ 归档成功 (归档ID: {archive.id})")
                success_count += 1
            else:
                print(f"  [模拟] 将被归档")
                success_count += 1

            print()

        except Exception as e:
            print(f"  ✗ 归档失败: {str(e)}\n")
            failed_count += 1
            failed_list.append(
                {
                    "project_no": project.project_no,
                    "title": project.title,
                    "error": str(e),
                }
            )

    # 输出统计信息
    print("=" * 60)
    print("归档完成统计:")
    print(f"  总数: {total_count}")
    print(f"  成功: {success_count}")
    print(f"  失败: {failed_count}")

    if failed_count > 0:
        print("\n失败列表:")
        for item in failed_list:
            print(f"  - {item['project_no']}: {item['title']}")
            print(f"    错误: {item['error']}")

    print("=" * 60)


def archive_by_batch(batch_code, dry_run=False):
    """
    按批次归档项目
    :param batch_code: 批次编码
    :param dry_run: 是否为试运行模式
    """
    from apps.system_settings.models import ProjectBatch

    try:
        batch = ProjectBatch.objects.get(code=batch_code)
    except ProjectBatch.DoesNotExist:
        print(f"错误：批次 {batch_code} 不存在")
        return

    print(f"{'[试运行]' if dry_run else '[执行]'} 归档批次: {batch.name}\n")

    # 查找该批次下所有已结题项目
    projects_to_archive = Project.objects.filter(
        batch=batch, status=Project.ProjectStatus.CLOSED, is_deleted=False
    ).exclude(id__in=ProjectArchive.objects.values_list("project_id", flat=True))

    total_count = projects_to_archive.count()
    print(f"找到 {total_count} 个需要归档的项目\n")

    if total_count == 0:
        print("该批次没有需要归档的项目")
        return

    success_count = 0
    failed_count = 0

    for project in projects_to_archive:
        try:
            print(f"归档项目: {project.project_no} - {project.title}")

            if not dry_run:
                archive = ArchiveService.archive_project(project)
                print(f"  ✓ 成功 (归档ID: {archive.id})\n")
                success_count += 1
            else:
                print(f"  [模拟] 将被归档\n")
                success_count += 1

        except Exception as e:
            print(f"  ✗ 失败: {str(e)}\n")
            failed_count += 1

    print("=" * 60)
    print(f"归档统计: 成功 {success_count}, 失败 {failed_count}")
    print("=" * 60)


def clean_old_archives(years=5, dry_run=False):
    """
    清理过期的归档数据
    :param years: 保留多少年的归档数据
    :param dry_run: 是否为试运行模式
    """
    print(f"{'[试运行]' if dry_run else '[执行]'} 清理 {years} 年前的归档数据...\n")

    cutoff_date = timezone.now() - timedelta(days=years * 365)

    old_archives = ProjectArchive.objects.filter(archived_at__lt=cutoff_date)

    count = old_archives.count()
    print(f"找到 {count} 条过期归档记录\n")

    if count == 0:
        print("没有需要清理的归档数据")
        return

    if not dry_run:
        # 逐条删除，记录日志
        for archive in old_archives:
            print(
                f"删除归档: {archive.project.project_no if archive.project else 'N/A'}"
            )
            archive.delete()
        print(f"\n✓ 已删除 {count} 条归档记录")
    else:
        for archive in old_archives:
            print(
                f"[模拟] 将删除: {archive.project.project_no if archive.project else 'N/A'}"
            )
        print(f"\n[模拟] 将删除 {count} 条归档记录")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="项目自动归档脚本")
    parser.add_argument(
        "--mode",
        choices=["auto", "batch", "clean"],
        default="auto",
        help="运行模式: auto(自动归档), batch(按批次归档), clean(清理过期归档)",
    )
    parser.add_argument(
        "--months", type=int, default=6, help="结题后多少个月进行自动归档（默认6个月）"
    )
    parser.add_argument("--batch", type=str, help="批次编码（batch模式必需）")
    parser.add_argument(
        "--years",
        type=int,
        default=5,
        help="清理多少年前的归档数据（clean模式使用，默认5年）",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="试运行模式，不实际执行操作"
    )

    args = parser.parse_args()

    try:
        if args.mode == "auto":
            auto_archive_projects(
                months_after_closure=args.months, dry_run=args.dry_run
            )
        elif args.mode == "batch":
            if not args.batch:
                print("错误：batch模式需要指定--batch参数")
                sys.exit(1)
            archive_by_batch(batch_code=args.batch, dry_run=args.dry_run)
        elif args.mode == "clean":
            clean_old_archives(years=args.years, dry_run=args.dry_run)
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
