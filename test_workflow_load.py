#!/usr/bin/env python
"""测试工作流加载"""

import os
import sys
import django
import json

# 设置 Django 环境
sys.path.insert(0, "/home/kai-wang/Code/Projects/dachuang-ms/backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import Client
from apps.users.models import User

# 创建测试客户端
client = Client()

# 获取一级管理员
admin = User.objects.filter(role_fk__code="LEVEL1_ADMIN").first()
if admin:
    # 登录
    response = client.post(
        "/api/v1/auth/login/",
        {"employee_id": admin.employee_id, "password": "123456"},
        content_type="application/json",
    )

    if response.status_code == 200:
        data = response.json()
        token = data.get("data", {}).get("access_token")

        headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

        # 获取工作流
        response = client.get(
            "/api/v1/system-settings/batch-workflows/4/workflows/APPLICATION/",
            **headers,
        )
        print(f"Workflow response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✓ Workflow loaded successfully")
            print(f"\nWorkflow details:")
            print(f"  Name: {result.get('name')}")
            print(f"  Phase: {result.get('phase')}")
            print(f"  Nodes count: {result.get('node_count')}")

            nodes = result.get("nodes", [])
            print(f"\nNodes ({len(nodes)}):")
            for node in nodes:
                print(
                    f"  - {node['id']}: {node['name']} ({node['node_type']}) - Role: {node.get('role_code', 'N/A')}"
                )
        else:
            print(f"Error: {response.content.decode()}")
