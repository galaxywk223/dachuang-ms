"""
系统设置服务
"""

from datetime import datetime

from .models import SystemSetting, ProjectBatch


DEFAULT_SETTINGS = {
    "APPLICATION_WINDOW": {
        "enabled": False,
        "start": "",
        "end": "",
    },
    "MIDTERM_WINDOW": {
        "enabled": False,
        "start": "",
        "end": "",
    },
    "CLOSURE_WINDOW": {
        "enabled": False,
        "start": "",
        "end": "",
    },
    "REVIEW_WINDOW": {
        "application": {
            "teacher": {"enabled": False, "start": "", "end": ""},
            "level2": {"enabled": False, "start": "", "end": ""},
            "level1": {"enabled": False, "start": "", "end": ""},
        },
        "midterm": {
            "teacher": {"enabled": False, "start": "", "end": ""},
            "level2": {"enabled": False, "start": "", "end": ""},
        },
        "closure": {
            "teacher": {"enabled": False, "start": "", "end": ""},
            "level2": {"enabled": False, "start": "", "end": ""},
            "level1": {"enabled": False, "start": "", "end": ""},
        },
    },
    "LIMIT_RULES": {
        "max_advisors": 2,
        "max_members": 5,
        "max_teacher_active": 5,
        "max_student_active": 1,
        "max_student_member": 1,
        "teacher_excellent_bonus": 0,
        "college_quota": {},
        "dedupe_title": True,
        "advisor_title_required": False,
    },
    "PROCESS_RULES": {
        "allow_active_reapply": False,
        "reject_to_previous": False,
        "show_material_in_closure_review": True,
    },
    "REVIEW_RULES": {
        "teacher_application_comment_min": 0,
    },
}


class SystemSettingService:
    """
    系统设置读取辅助
    """

    @staticmethod
    def get_current_batch():
        current = ProjectBatch.objects.filter(is_current=True, is_active=True).first()
        if current:
            return current
        return ProjectBatch.objects.filter(is_active=True).order_by("-year", "-id").first()

    @staticmethod
    def get_setting(code, default=None, batch=None):
        batch_obj = batch
        if batch_obj is None:
            batch_obj = SystemSettingService.get_current_batch()
        elif isinstance(batch_obj, int):
            batch_obj = ProjectBatch.objects.filter(id=batch_obj).first()
        elif isinstance(batch_obj, str) and batch_obj.isdigit():
            batch_obj = ProjectBatch.objects.filter(id=int(batch_obj)).first()

        setting = None
        if batch_obj:
            setting = SystemSetting.objects.filter(
                code=code, is_active=True, batch=batch_obj
            ).first()
        if setting is None:
            setting = SystemSetting.objects.filter(
                code=code, is_active=True, batch__isnull=True
            ).first()
        base = default or DEFAULT_SETTINGS.get(code, {})
        if setting:
            merged = dict(base)
            merged.update(setting.data or {})
            return merged
        return base

    @staticmethod
    def _parse_date(value):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def check_window(code, now_date, batch=None):
        data = SystemSettingService.get_setting(code, batch=batch)
        if not data.get("enabled"):
            return True, ""

        start = SystemSettingService._parse_date(data.get("start"))
        end = SystemSettingService._parse_date(data.get("end"))

        if start and now_date < start:
            return False, "当前未到开放时间"
        if end and now_date > end:
            return False, "当前已超过截止时间"
        return True, ""

    @staticmethod
    def check_review_window(review_type, review_level, now_date, batch=None):
        data = SystemSettingService.get_setting("REVIEW_WINDOW", batch=batch)
        level_key = review_level.lower()
        type_map = {
            "APPLICATION": "application",
            "MID_TERM": "midterm",
            "CLOSURE": "closure",
        }
        type_key = type_map.get(review_type, review_type.lower())
        if type_key not in data:
            return True, ""
        level_data = data.get(type_key, {}).get(level_key, {})
        if not level_data.get("enabled"):
            return True, ""
        start = SystemSettingService._parse_date(level_data.get("start"))
        end = SystemSettingService._parse_date(level_data.get("end"))
        if start and now_date < start:
            return False, "当前未到审核开放时间"
        if end and now_date > end:
            return False, "当前已超过审核截止时间"
        return True, ""
