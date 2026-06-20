from pathlib import PurePosixPath, PureWindowsPath
import re

from django.core.exceptions import SuspiciousFileOperation
from django.http import FileResponse
from rest_framework import status
from rest_framework.response import Response


SAFE_DOWNLOAD_FILENAME_RE = re.compile(r'[\x00-\x1f\x7f<>:"\\|?*/]')


def safe_download_filename(value, fallback="download"):
    raw = str(value or "").replace("\\", "/")
    filename = PureWindowsPath(PurePosixPath(raw).name).name
    filename = filename.lstrip(". ")
    filename = SAFE_DOWNLOAD_FILENAME_RE.sub("_", filename)
    filename = re.sub(r"\.+(?=_)", "", filename)
    filename = filename.strip().strip(". ")
    return filename or fallback


def attachment_content_disposition(filename, fallback="download"):
    safe_filename = safe_download_filename(filename, fallback)
    return f'attachment; filename="{safe_filename}"'


def file_field_download_response(file_field, *, missing_message):
    if not file_field:
        return Response(
            {"code": 404, "message": missing_message},
            status=status.HTTP_404_NOT_FOUND,
        )

    filename = safe_download_filename(file_field.name, fallback="")
    if not filename:
        return Response(
            {"code": 404, "message": missing_message},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        stream = file_field.open("rb")
    except (FileNotFoundError, OSError, SuspiciousFileOperation, ValueError):
        return Response(
            {"code": 404, "message": missing_message},
            status=status.HTTP_404_NOT_FOUND,
        )

    return FileResponse(stream, as_attachment=True, filename=filename)
