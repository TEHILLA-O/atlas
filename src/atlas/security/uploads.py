"""Upload validation: size, type and filename hygiene."""

from __future__ import annotations

from pathlib import Path

from atlas.config.settings import Settings

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx", ".html", ".htm"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/html",
    "application/octet-stream",
}


class UploadRejectedError(ValueError):
    """Raised when an upload fails policy checks."""


def validate_upload(
    filename: str,
    content_type: str | None,
    size: int,
    settings: Settings,
) -> str:
    if size <= 0:
        raise UploadRejectedError("empty upload")
    if size > settings.max_upload_bytes:
        raise UploadRejectedError(f"file exceeds {settings.max_upload_mb} MB limit")
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise UploadRejectedError(f"unsupported file type: {suffix or 'unknown'}")
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise UploadRejectedError(f"unsupported content type: {content_type}")
    safe_name = Path(filename).name.replace("..", "")
    if not safe_name:
        raise UploadRejectedError("invalid filename")
    return safe_name
