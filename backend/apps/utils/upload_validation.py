from pathlib import Path, PurePosixPath, PureWindowsPath

from rest_framework import serializers


GENERIC_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
DOCUMENT_TEMPLATE_EXTENSIONS = {".doc", ".docx", ".pdf"}
PLATFORM_MATERIAL_EXTENSIONS = GENERIC_IMAGE_EXTENSIONS | {
    ".doc",
    ".docx",
    ".pdf",
    ".ppt",
    ".pptx",
    ".rar",
    ".xls",
    ".xlsx",
    ".zip",
}


def _display_extensions(extensions):
    return "/".join(sorted(ext.lstrip(".") for ext in extensions))


def _uploaded_basename(uploaded_file):
    raw_name = str(getattr(uploaded_file, "name", "") or "")
    basename = PureWindowsPath(PurePosixPath(raw_name).name).name
    if not basename or basename in {".", ".."}:
        return "", raw_name
    return basename, raw_name


def validate_uploaded_file(
    uploaded_file,
    *,
    label,
    allowed_extensions,
    max_size_mb,
    empty_as_none=False,
    error_class=serializers.ValidationError,
):
    if not uploaded_file:
        return None

    basename, _ = _uploaded_basename(uploaded_file)
    if not basename:
        raise error_class(f"{label}文件名无效")
    uploaded_file.name = basename

    size = getattr(uploaded_file, "size", 0) or 0
    if size == 0:
        if empty_as_none:
            return None
        raise error_class(f"{label}不能为空")

    suffix = Path(basename).suffix.lower()
    if suffix not in allowed_extensions:
        extensions = _display_extensions(allowed_extensions)
        raise error_class(f"{label}仅支持 {extensions} 格式")

    max_size = max_size_mb * 1024 * 1024
    if size > max_size:
        raise error_class(f"{label}文件大小不能超过{max_size_mb}MB")

    return uploaded_file


def validate_image_file(
    uploaded_file,
    *,
    label,
    max_size_mb=5,
    empty_as_none=False,
    error_class=serializers.ValidationError,
):
    return validate_uploaded_file(
        uploaded_file,
        label=label,
        allowed_extensions=GENERIC_IMAGE_EXTENSIONS,
        max_size_mb=max_size_mb,
        empty_as_none=empty_as_none,
        error_class=error_class,
    )


def validate_document_template_file(
    uploaded_file,
    *,
    label="模板文件",
    max_size_mb=5,
    empty_as_none=False,
    error_class=serializers.ValidationError,
):
    return validate_uploaded_file(
        uploaded_file,
        label=label,
        allowed_extensions=DOCUMENT_TEMPLATE_EXTENSIONS,
        max_size_mb=max_size_mb,
        empty_as_none=empty_as_none,
        error_class=error_class,
    )


def validate_platform_material_file(
    uploaded_file,
    *,
    label="资料",
    max_size_mb=20,
    empty_as_none=False,
    error_class=serializers.ValidationError,
):
    return validate_uploaded_file(
        uploaded_file,
        label=label,
        allowed_extensions=PLATFORM_MATERIAL_EXTENSIONS,
        max_size_mb=max_size_mb,
        empty_as_none=empty_as_none,
        error_class=error_class,
    )


class ValidatedImageField(serializers.ImageField):
    def __init__(self, *args, label, max_size_mb=5, **kwargs):
        self.validation_label = label
        self.max_size_mb = max_size_mb
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        data = validate_image_file(
            data,
            label=self.validation_label,
            max_size_mb=self.max_size_mb,
        )
        if data is None:
            return None
        return serializers.FileField.to_internal_value(self, data)
