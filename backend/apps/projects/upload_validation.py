from rest_framework import serializers

from apps.utils.upload_validation import validate_uploaded_file


PROJECT_DOCUMENT_EXTENSIONS = {".doc", ".docx", ".pdf"}
PROJECT_SUPPORT_EXTENSIONS = PROJECT_DOCUMENT_EXTENSIONS | {
    ".jpg",
    ".jpeg",
    ".png",
    ".rar",
    ".xls",
    ".xlsx",
    ".zip",
}


def validate_project_document_file(
    uploaded_file,
    *,
    label,
    max_size_mb,
    empty_as_none=False,
    error_class=serializers.ValidationError,
):
    return validate_uploaded_file(
        uploaded_file,
        label=label,
        allowed_extensions=PROJECT_DOCUMENT_EXTENSIONS,
        max_size_mb=max_size_mb,
        empty_as_none=empty_as_none,
        error_class=error_class,
    )


def validate_project_support_file(
    uploaded_file,
    *,
    label,
    max_size_mb,
    empty_as_none=False,
    error_class=serializers.ValidationError,
):
    return validate_uploaded_file(
        uploaded_file,
        label=label,
        allowed_extensions=PROJECT_SUPPORT_EXTENSIONS,
        max_size_mb=max_size_mb,
        empty_as_none=empty_as_none,
        error_class=error_class,
    )
