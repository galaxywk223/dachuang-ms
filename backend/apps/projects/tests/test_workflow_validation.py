from decimal import Decimal

from django.test import SimpleTestCase
from django.test import TestCase

from apps.dictionaries.models import DictionaryItem, DictionaryType
from apps.projects.views.mixins.project_workflow_mixin import (
    parse_optional_budget,
    parse_optional_node_id,
)
from apps.projects.services.closure_service import (
    _parse_achievements_payload,
    _validate_closure_achievements,
)


class ProjectWorkflowValidationTestCase(SimpleTestCase):
    def test_parse_optional_budget_preserves_decimal_precision(self):
        amount = parse_optional_budget("0.10", "经费格式错误")

        self.assertEqual(amount, Decimal("0.10"))

    def test_parse_optional_budget_accepts_blank_as_none(self):
        self.assertIsNone(parse_optional_budget("", "经费格式错误"))
        self.assertIsNone(parse_optional_budget(None, "经费格式错误"))

    def test_parse_optional_budget_rejects_invalid_value(self):
        with self.assertRaisesMessage(ValueError, "经费格式错误"):
            parse_optional_budget("invalid", "经费格式错误")

    def test_parse_optional_budget_rejects_negative_value(self):
        with self.assertRaisesMessage(ValueError, "经费格式错误"):
            parse_optional_budget("-1", "经费格式错误")

    def test_parse_optional_budget_rejects_non_finite_value(self):
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value):
                with self.assertRaisesMessage(ValueError, "经费格式错误"):
                    parse_optional_budget(value, "经费格式错误")

    def test_parse_optional_node_id_accepts_positive_integer(self):
        self.assertEqual(parse_optional_node_id("12", "节点格式错误"), 12)

    def test_parse_optional_node_id_accepts_blank_as_none(self):
        self.assertIsNone(parse_optional_node_id("", "节点格式错误"))
        self.assertIsNone(parse_optional_node_id(None, "节点格式错误"))

    def test_parse_optional_node_id_rejects_invalid_value(self):
        with self.assertRaisesMessage(ValueError, "节点格式错误"):
            parse_optional_node_id("bad", "节点格式错误")

    def test_parse_optional_node_id_rejects_non_positive_value(self):
        with self.assertRaisesMessage(ValueError, "节点格式错误"):
            parse_optional_node_id("0", "节点格式错误")

    def test_parse_achievements_payload_accepts_json_list(self):
        payload = _parse_achievements_payload(
            {"achievements_json": '[{"title": "成果", "achievement_type": "PAPER"}]'}
        )

        self.assertEqual(payload[0]["title"], "成果")

    def test_parse_achievements_payload_accepts_achievements_json_string(self):
        payload = _parse_achievements_payload(
            {"achievements": '[{"title": "成果", "achievement_type": "PAPER"}]'}
        )

        self.assertEqual(payload[0]["title"], "成果")

    def test_parse_achievements_payload_rejects_invalid_json(self):
        with self.assertRaisesMessage(ValueError, "成果数据格式错误"):
            _parse_achievements_payload({"achievements_json": "[invalid"})

    def test_parse_achievements_payload_rejects_invalid_achievements_json_string(self):
        with self.assertRaisesMessage(ValueError, "成果数据格式错误"):
            _parse_achievements_payload({"achievements": "[invalid"})

    def test_parse_achievements_payload_rejects_non_object_items(self):
        with self.assertRaisesMessage(ValueError, "成果数据格式错误"):
            _parse_achievements_payload({"achievements_json": '["bad"]'})


class ClosureAchievementValidationTestCase(TestCase):
    def setUp(self):
        self.achievement_type = DictionaryType.objects.create(
            code="achievement_type",
            name="成果类型",
            is_active=True,
        )
        self.paper_type = DictionaryItem.objects.create(
            dict_type=self.achievement_type,
            value="PAPER",
            label="论文",
            is_active=True,
        )

    def test_validate_closure_achievements_accepts_active_type(self):
        _validate_closure_achievements(
            [{"title": "成果", "achievement_type": self.paper_type.id}]
        )

    def test_validate_closure_achievements_rejects_missing_type(self):
        with self.assertRaisesMessage(ValueError, "成果类型不存在"):
            _validate_closure_achievements([{"title": "成果"}])

    def test_validate_closure_achievements_rejects_unknown_type(self):
        with self.assertRaisesMessage(ValueError, "成果类型不存在"):
            _validate_closure_achievements(
                [{"title": "成果", "achievement_type": "UNKNOWN"}]
            )

    def test_validate_closure_achievements_rejects_inactive_type(self):
        inactive_type = DictionaryItem.objects.create(
            dict_type=self.achievement_type,
            value="INACTIVE",
            label="停用成果",
            is_active=False,
        )

        with self.assertRaisesMessage(ValueError, "成果类型不存在"):
            _validate_closure_achievements(
                [{"title": "成果", "achievement_type": inactive_type.id}]
            )
