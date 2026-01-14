# mypy: disable-error-code=var-annotated
"""
审核相关常量定义
由于 Review.ReviewLevel 枚举已删除，改为使用字符串常量
"""

# 常用的审核级别/角色标识
# 这些是向后兼容的常量，新角色不需要在这里定义
REVIEW_LEVEL_TEACHER = "TEACHER"
REVIEW_LEVEL_LEVEL2 = "LEVEL2"
REVIEW_LEVEL_LEVEL1 = "LEVEL1"

# 旧的枚举映射 - 用于向后兼容
LEGACY_REVIEW_LEVELS = {
    "TEACHER": "TEACHER",
    "LEVEL2": "LEVEL2",
    "LEVEL1": "LEVEL1",
    "LEVEL2_ADMIN": "LEVEL2",
    "LEVEL1_ADMIN": "LEVEL1",
}


def normalize_review_level(level_or_role):
    """
    将角色代码规范化为 review_level
    保持向后兼容性
    """
    if not level_or_role:
        return "UNKNOWN"

    # 直接返回已知的标准值
    standard_levels = {"TEACHER", "LEVEL1", "LEVEL2"}
    if level_or_role in standard_levels:
        return level_or_role

    # 映射常见角色代码到审核级别
    role_map = {
        "TEACHER": "TEACHER",
        "LEVEL1_ADMIN": "LEVEL1",
        "LEVEL2_ADMIN": "LEVEL2",
        "COLLEGE_ADMIN": "LEVEL2",
        "SCHOOL_ADMIN": "LEVEL1",
    }
    return role_map.get(level_or_role, level_or_role)
