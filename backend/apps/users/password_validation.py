"""
用户密码强度校验工具。
"""

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


def get_password_validation_errors(password, user=None):
    try:
        validate_password(password, user=user)
    except DjangoValidationError as exc:
        return list(exc.messages)
    return []
