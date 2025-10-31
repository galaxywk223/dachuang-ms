"""
创建初始测试数据
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "创建初始测试数据"

    def handle(self, *args, **options):
        # 创建测试用户
        if not User.objects.filter(username="wangkai").exists():
            user = User.objects.create_user(
                username="wangkai",
                employee_id="20210001",
                real_name="王凯",
                password="123456",
                role=User.UserRole.STUDENT,
                email="wangkai@example.com",
                phone="13800138000",
                major="计算机科学与技术",
                grade="2021",
                class_name="计算机1班",
                college="计算机学院",
            )
            self.stdout.write(self.style.SUCCESS(f"成功创建用户: {user.real_name}"))
        else:
            self.stdout.write(self.style.WARNING("用户 wangkai 已存在"))

        # 创建二级管理员（教师）
        if not User.objects.filter(username="teacher01").exists():
            teacher = User.objects.create_user(
                username="teacher01",
                employee_id="T20210001",
                real_name="李老师",
                password="123456",
                role=User.UserRole.LEVEL2_ADMIN,
                email="teacher01@example.com",
                phone="13800138001",
                college="计算机学院",
                department="软件工程系",
            )
            self.stdout.write(
                self.style.SUCCESS(f"成功创建二级管理员: {teacher.real_name}")
            )
        else:
            self.stdout.write(self.style.WARNING("用户 teacher01 已存在"))

        # 创建一级管理员
        if not User.objects.filter(username="admin01").exists():
            admin = User.objects.create_user(
                username="admin01",
                employee_id="A20210001",
                real_name="张主任",
                password="123456",
                role=User.UserRole.LEVEL1_ADMIN,
                email="admin01@example.com",
                phone="13800138002",
                college="教务处",
                department="教学管理科",
            )
            self.stdout.write(
                self.style.SUCCESS(f"成功创建一级管理员: {admin.real_name}")
            )
        else:
            self.stdout.write(self.style.WARNING("用户 admin01 已存在"))

        self.stdout.write(self.style.SUCCESS("初始化数据完成！"))
        self.stdout.write(self.style.SUCCESS("测试账号:"))
        self.stdout.write("  学生: wangkai / 123456")
        self.stdout.write("  二级管理员: teacher01 / 123456")
        self.stdout.write("  一级管理员: admin01 / 123456")
