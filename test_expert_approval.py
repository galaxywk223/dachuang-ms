#!/usr/bin/env python
"""用专家测试审查审批功能"""

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

# 获取专家
expert = User.objects.filter(role_fk__code="EXPERT").first()
if expert:
    print(f"Found expert: {expert.real_name} ({expert.employee_id})")

    # 登录
    response = client.post(
        "/api/v1/auth/login/",
        {"employee_id": expert.employee_id, "password": "123456"},
        content_type="application/json",
    )

    if response.status_code == 200:
        data = response.json()
        token = data.get("data", {}).get("access_token")
        if token:
            print(f"Expert login successful")

            headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

            # 获取分配给这个专家的待审查
            review = Review.objects.filter(status="PENDING", reviewer=expert).first()
            if review:
                print(f"Found review: {review.id} (status: {review.status})")

                # 尝试审批
                payload = {"action": "approve", "comments": "Looks good!"}

                response = client.post(
                    f"/api/v1/reviews/{review.id}/review/",
                    json.dumps(payload),
                    content_type="application/json",
                    **headers,
                )
                print(f"\nApproval response status: {response.status_code}")
                response_text = response.content.decode()

                if response.status_code == 200:
                    print("✓ Review approved successfully!")
                    result = response.json()
                    print(
                        f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}"
                    )
                else:
                    print(f"Error response: {response_text}")
            else:
                print("No pending review for this expert")
        else:
            print(f"Login failed")
    else:
        print(f"Login failed with status: {response.status_code}")
else:
    print("No expert found")
