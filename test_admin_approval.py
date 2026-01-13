#!/usr/bin/env python
"""用一级管理员测试审查审批功能"""

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
from apps.reviews.models import Review

# 创建测试客户端
client = Client()

# 获取二级管理员
admin = User.objects.filter(role_fk__code="LEVEL2_ADMIN").first()
if admin:
    print(f"Found admin: {admin.real_name} ({admin.employee_id})")

    # 登录
    response = client.post(
        "/api/v1/auth/login/",
        {"employee_id": admin.employee_id, "password": "123456"},
        content_type="application/json",
    )

    if response.status_code == 200:
        data = response.json()
        token = data.get("data", {}).get("access_token")
        if token:
            print(f"Admin login successful")

            headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

            # 获取审查
            review = Review.objects.filter(
                status="PENDING", review_level="LEVEL2"
            ).first()
            if review:
                print(f"Found review: {review.id} (status: {review.status})")

                # 尝试审批
                payload = {"status": "APPROVED", "comments": "Approved by admin"}

                response = client.post(
                    f"/api/v1/reviews/{review.id}/review/",
                    json.dumps(payload),
                    content_type="application/json",
                    **headers,
                )
                print(f"Approval response status: {response.status_code}")
                print(f"Response headers: {dict(response.items())}")
                response_text = response.content.decode()
                print(f"Response body: {response_text}")
                if response.status_code != 200:
                    print(f"Error!")
            else:
                print("No pending review found")
        else:
            print(f"Login failed: {response.content.decode()}")
    else:
        print(f"Login failed with status: {response.status_code}")
else:
    print("No admin found")
