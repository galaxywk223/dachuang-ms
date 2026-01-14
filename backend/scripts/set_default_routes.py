#!/usr/bin/env python
"""
设置角色的默认路由
"""

import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import Role, User

# 定义角色对应的默认路由
ROLE_ROUTES = {
    User.UserRole.STUDENT: "/establishment/apply",
    User.UserRole.TEACHER: "/teacher/dashboard",
    User.UserRole.EXPERT: "/teacher/dashboard",  # 专家和教师用同一个页面
    User.UserRole.LEVEL1_ADMIN: "/level1-admin/statistics",
    User.UserRole.LEVEL2_ADMIN: "/level2-admin/projects",
}


def set_default_routes():
    """为所有角色设置默认路由"""
    print("开始设置角色默认路由...")

    roles = Role.objects.all()
    updated_count = 0

    for role in roles:
        old_route = role.default_route

        # 如果角色代码在预定义的路由映射中
        if role.code in ROLE_ROUTES:
            role.default_route = ROLE_ROUTES[role.code]
        # 如果是有scope_dimension的管理员角色，使用二级管理员路由
        elif role.scope_dimension:
            role.default_route = "/level2-admin/projects"
        # 其他情况保持为空或设置默认值
        elif not role.default_route:
            role.default_route = ""

        # 如果有变化，保存
        if role.default_route != old_route:
            role.save(update_fields=["default_route"])
            updated_count += 1
            print(
                f"✓ 更新角色 {role.name}({role.code}): '{old_route}' -> '{role.default_route}'"
            )
        else:
            print(f"- 跳过角色 {role.name}({role.code}): 路由未变化")

    print(f"\n完成！共更新 {updated_count} 个角色的默认路由")


if __name__ == "__main__":
    set_default_routes()
