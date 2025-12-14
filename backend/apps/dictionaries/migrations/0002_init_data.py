"""
数据字典初始数据迁移
将所有硬编码的下拉选项数据导入数据库
"""

from django.db import migrations


def init_dictionary_data(apps, schema_editor):
    """
    初始化所有数据字典数据
    """
    DictionaryType = apps.get_model("dictionaries", "DictionaryType")
    DictionaryItem = apps.get_model("dictionaries", "DictionaryItem")

    # 定义所有字典类型和条目
    dictionaries = [
        # 用户角色
        {
            "code": "user_role",
            "name": "用户角色",
            "description": "系统用户的角色类型",
            "is_system": True,
            "items": [
                {"value": "STUDENT", "label": "学生", "sort_order": 1},
                {"value": "LEVEL2_ADMIN", "label": "二级管理员", "sort_order": 2},
                {"value": "LEVEL1_ADMIN", "label": "一级管理员", "sort_order": 3},
            ],
        },
        # 项目状态
        {
            "code": "project_status",
            "name": "项目状态",
            "description": "项目在审批流程中的状态",
            "is_system": True,
            "items": [
                {"value": "DRAFT", "label": "草稿", "sort_order": 1},
                {"value": "SUBMITTED", "label": "已提交", "sort_order": 2},
                {"value": "LEVEL2_REVIEWING", "label": "二级审核中", "sort_order": 3},
                {"value": "LEVEL2_APPROVED", "label": "二级审核通过", "sort_order": 4},
                {"value": "LEVEL2_REJECTED", "label": "二级审核不通过", "sort_order": 5},
                {"value": "LEVEL1_REVIEWING", "label": "一级审核中", "sort_order": 6},
                {"value": "LEVEL1_APPROVED", "label": "一级审核通过", "sort_order": 7},
                {"value": "LEVEL1_REJECTED", "label": "一级审核不通过", "sort_order": 8},
                {"value": "IN_PROGRESS", "label": "进行中", "sort_order": 9},
                {"value": "CLOSURE_DRAFT", "label": "结题草稿", "sort_order": 10},
                {"value": "CLOSURE_SUBMITTED", "label": "结题已提交", "sort_order": 11},
                {"value": "CLOSURE_LEVEL2_REVIEWING", "label": "结题二级审核中", "sort_order": 12},
                {"value": "CLOSURE_LEVEL2_APPROVED", "label": "结题二级审核通过", "sort_order": 13},
                {"value": "CLOSURE_LEVEL2_REJECTED", "label": "结题二级审核不通过", "sort_order": 14},
                {"value": "CLOSURE_LEVEL1_REVIEWING", "label": "结题一级审核中", "sort_order": 15},
                {"value": "CLOSURE_LEVEL1_APPROVED", "label": "结题一级审核通过", "sort_order": 16},
                {"value": "CLOSURE_LEVEL1_REJECTED", "label": "结题一级审核不通过", "sort_order": 17},
                {"value": "COMPLETED", "label": "已完成", "sort_order": 18},
                {"value": "CLOSED", "label": "已结题", "sort_order": 19},
            ],
        },
        # 项目级别
        {
            "code": "project_level",
            "name": "项目级别",
            "description": "大创项目的级别分类",
            "is_system": True,
            "items": [
                {"value": "NATIONAL", "label": "国家级", "sort_order": 1},
                {"value": "PROVINCIAL", "label": "省级", "sort_order": 2},
                {"value": "SCHOOL", "label": "校级", "sort_order": 3},
            ],
        },
        # 项目类别
        {
            "code": "project_category",
            "name": "项目类别",
            "description": "大创项目的类型分类",
            "is_system": True,
            "items": [
                {"value": "INNOVATION_TRAINING", "label": "创新训练项目", "sort_order": 1},
                {"value": "ENTREPRENEURSHIP_TRAINING", "label": "创业训练项目", "sort_order": 2},
                {"value": "ENTREPRENEURSHIP_PRACTICE", "label": "创业实践项目", "sort_order": 3},
            ],
        },
        # 项目成员角色
        {
            "code": "member_role",
            "name": "成员角色",
            "description": "项目成员在团队中的角色",
            "is_system": True,
            "items": [
                {"value": "LEADER", "label": "负责人", "sort_order": 1},
                {"value": "MEMBER", "label": "成员", "sort_order": 2},
            ],
        },
        # 成果类型
        {
            "code": "achievement_type",
            "name": "成果类型",
            "description": "项目研究成果的类型",
            "is_system": True,
            "items": [
                {"value": "PAPER", "label": "论文", "sort_order": 1},
                {"value": "PATENT", "label": "专利", "sort_order": 2},
                {"value": "SOFTWARE_COPYRIGHT", "label": "软件著作权", "sort_order": 3},
                {"value": "COMPETITION_AWARD", "label": "竞赛奖项", "sort_order": 4},
                {"value": "OTHER", "label": "其他", "sort_order": 5},
            ],
        },
        # 审核类型
        {
            "code": "review_type",
            "name": "审核类型",
            "description": "审核流程的类型",
            "is_system": True,
            "items": [
                {"value": "APPLICATION", "label": "申报审核", "sort_order": 1},
                {"value": "CLOSURE", "label": "结题审核", "sort_order": 2},
            ],
        },
        # 审核级别
        {
            "code": "review_level",
            "name": "审核级别",
            "description": "审核的层级",
            "is_system": True,
            "items": [
                {"value": "LEVEL2", "label": "二级审核", "sort_order": 1},
                {"value": "LEVEL1", "label": "一级审核", "sort_order": 2},
            ],
        },
        # 审核状态
        {
            "code": "review_status",
            "name": "审核状态",
            "description": "审核记录的状态",
            "is_system": True,
            "items": [
                {"value": "PENDING", "label": "待审核", "sort_order": 1},
                {"value": "APPROVED", "label": "审核通过", "sort_order": 2},
                {"value": "REJECTED", "label": "审核不通过", "sort_order": 3},
            ],
        },
        # 结题评价等级
        {
            "code": "closure_rating",
            "name": "结题评价等级",
            "description": "项目结题时的评价等级",
            "is_system": True,
            "items": [
                {"value": "EXCELLENT", "label": "优秀", "sort_order": 1},
                {"value": "GOOD", "label": "良好", "sort_order": 2},
                {"value": "QUALIFIED", "label": "合格", "sort_order": 3},
                {"value": "UNQUALIFIED", "label": "不合格", "sort_order": 4},
                {"value": "DEFERRED", "label": "延期", "sort_order": 5},
            ],
        },
        # 通知类型
        {
            "code": "notification_type",
            "name": "通知类型",
            "description": "系统通知的类型",
            "is_system": True,
            "items": [
                {"value": "SYSTEM", "label": "系统通知", "sort_order": 1},
                {"value": "PROJECT", "label": "项目通知", "sort_order": 2},
                {"value": "REVIEW", "label": "审核通知", "sort_order": 3},
            ],
        },
    ]

    # 创建字典类型和条目
    for dict_data in dictionaries:
        items = dict_data.pop("items")
        dict_type = DictionaryType.objects.create(**dict_data)

        for item_data in items:
            DictionaryItem.objects.create(dict_type=dict_type, **item_data)


def reverse_init_dictionary_data(apps, schema_editor):
    """
    反向迁移：删除所有初始化的字典数据
    """
    DictionaryType = apps.get_model("dictionaries", "DictionaryType")
    DictionaryType.objects.filter(is_system=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("dictionaries", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(init_dictionary_data, reverse_init_dictionary_data),
    ]
