from io import BytesIO
import zipfile

from django.test import SimpleTestCase

from apps.utils.export import generate_zip, safe_zip_arcname, safe_zip_path


class StorageBackedFile:
    name = "remote/proposal.pdf"

    @property
    def path(self):
        raise NotImplementedError("Remote storage has no local path")

    def open(self, mode="rb"):
        return BytesIO(b"remote-content")


class ExportZipSafetyTestCase(SimpleTestCase):
    def test_safe_zip_arcname_removes_traversal_segments(self):
        self.assertEqual(
            safe_zip_arcname("../外部/..\\evil:name?.docx"),
            "外部/evil_name_.docx",
        )

    def test_safe_zip_path_keeps_supplied_segments_only(self):
        self.assertEqual(
            safe_zip_path("P001_项目/../标题", "成果", "../论文?.pdf"),
            "P001_项目_标题/成果/论文_.pdf",
        )

    def test_generate_zip_streams_storage_backed_file_fields(self):
        output = generate_zip([(StorageBackedFile(), "../unsafe?.pdf")])

        with zipfile.ZipFile(output) as archive:
            self.assertEqual(archive.namelist(), ["unsafe_.pdf"])
            self.assertEqual(archive.read("unsafe_.pdf"), b"remote-content")

    def test_generate_zip_skips_missing_disk_paths(self):
        output = generate_zip([("missing-file.pdf", "missing.pdf")])

        with zipfile.ZipFile(output) as archive:
            self.assertEqual(archive.namelist(), [])
