#!/usr/bin/env python
"""测试审查审批功能"""

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

# 获取一个学生用户进行登录
try:
    student = User.objects.filter(role_fk__code="STUDENT").first()
    if student:
        print(f"Found student: {student.real_name} ({student.employee_id})")

        # 登录
        response = client.post(
            "/api/v1/auth/login/",
            {"employee_id": student.employee_id, "password": "123456"},
            content_type="application/json",
        )

        if response.status_code == 200:
            data = response.json()
            # 响应结构: {"code": 200, "data": {"access_token": "...", ...}}
            token = data.get("data", {}).get("access_token")
            if token:
                print(f"Login successful, token: {token[:20]}...")
            else:
                print(f"Login response: {response.content.decode()}")
                sys.exit(1)

            # 获取待审查的评论（首先尝试教师角色）
            teacher = User.objects.filter(role_fk__code="TEACHER").first()
            if teacher:
                # 用教师身份登录
                response = client.post(
                    "/api/v1/auth/login/",
                    {"employee_id": teacher.employee_id, "password": "123456"},
                    content_type="application/json",
                )

                if response.status_code == 200:
                    data = response.json()
                    teacher_token = data.get("data", {}).get("access_token")
                    headers = {"HTTP_AUTHORIZATION": f"Bearer {teacher_token}"}
                    print(f"Teacher login successful")

                    # 获取待审查的评论
                    response = client.get(
                        "/api/v1/reviews/?status=PENDING&review_level=TEACHER",
                        **headers,
                    )
                    print(f"Teacher reviews response status: {response.status_code}")

                    if response.status_code == 200:
                        reviews = response.json()
                        if isinstance(reviews, list) and reviews:
                            print(f"Found {len(reviews)} reviews for teacher")
                            review = reviews[0]
                            review_id = review.get("id")
                            print(f"Found review {review_id}")

                            # 尝试审批评论
                            payload = {"status": "APPROVED", "comments": "Looks good!"}

                            response = client.post(
                                f"/api/v1/reviews/{review_id}/review/",
                                json.dumps(payload),
                                content_type="application/json",
                                **headers,
                            )
                            print(f"Approval response status: {response.status_code}")
                            if response.status_code != 200:
                                print(f"Response: {response.content.decode()}")
                            else:
                                print("✓ Review approved successfully!")
                        else:
                            print(
                                f"No pending reviews for teacher, checking for any review..."
                            )
                            # 直接尝试审批 ID=22 的审查
                            payload = {
                                "status": "APPROVED",
                                "comments": "Test approval",
                            }

                            response = client.post(
                                f"/api/v1/reviews/22/review/",
                                json.dumps(payload),
                                content_type="application/json",
                                **headers,
                            )
                            print(f"Approval response status: {response.status_code}")
                            print(f"Response: {response.content.decode()}")
                else:
                    print(f"Teacher login failed: {response.content.decode()}")
            else:
                print("No teacher found")
            print(f"Reviews response status: {response.status_code}")

            if response.status_code == 200:
                reviews = response.json()
                if isinstance(reviews, list) and reviews:
                    review = reviews[0]
                    review_id = review.get("id")
                    print(f"Found review {review_id}")

                    # 尝试审批评论
                    payload = {"status": "APPROVED", "comments": "Looks good!"}

                    response = client.post(
                        f"/api/v1/reviews/{review_id}/review/",
                        json.dumps(payload),
                        content_type="application/json",
                        **headers,
                    )
                    print(f"Approval response status: {response.status_code}")
                    print(f"Response: {response.content.decode()}")
                else:
                    print("No reviews found")
        else:
            print(f"Login failed: {response.content.decode()}")
    else:
        print("No student found")
except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
