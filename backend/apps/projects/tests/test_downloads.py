from io import BytesIO

from django.http import FileResponse
from django.test import SimpleTestCase
from rest_framework.response import Response

from apps.utils.downloads import (
    attachment_content_disposition,
    file_field_download_response,
    safe_download_filename,
)


class DownloadResponseTestCase(SimpleTestCase):
    def test_safe_download_filename_removes_paths_and_header_unsafe_chars(self):
        self.assertEqual(
            safe_download_filename('../unsafe:"name"?.xlsx'),
            "unsafe__name__.xlsx",
        )
        self.assertEqual(safe_download_filename("..."), "download")

    def test_attachment_content_disposition_uses_safe_filename(self):
        self.assertEqual(
            attachment_content_disposition("学院/../../bad:name?.zip"),
            'attachment; filename="bad_name_.zip"',
        )

    def test_file_field_download_response_returns_file_response(self):
        file_field = FakeFileField("nested/report.pdf", BytesIO(b"report"))

        response = file_field_download_response(
            file_field,
            missing_message="文件不存在",
        )

        self.assertIsInstance(response, FileResponse)
        self.assertEqual(response.filename, "report.pdf")

    def test_file_field_download_response_returns_404_when_storage_file_missing(self):
        file_field = FakeFileField("nested/report.pdf", OSError("missing"))

        response = file_field_download_response(
            file_field,
            missing_message="文件不存在",
        )

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"code": 404, "message": "文件不存在"})


class FakeFileField:
    def __init__(self, name, open_result):
        self.name = name
        self.open_result = open_result

    def __bool__(self):
        return bool(self.name)

    def open(self, mode):
        if isinstance(self.open_result, Exception):
            raise self.open_result
        return self.open_result
