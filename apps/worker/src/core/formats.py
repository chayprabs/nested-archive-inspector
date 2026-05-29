from __future__ import annotations

from pathlib import Path

SUPPORTED_READ_FORMATS = (
    "zip",
    "tar",
    "tar.gz",
    "tgz",
    "tar.zst",
    "tar.bz2",
    "tar.xz",
    "7z",
    "rar",
    "iso",
    "dmg",
    "cab",
    "cpio",
    "xar",
    "ar",
)


def detect_format(path: Path) -> str:
    name = path.name.lower()
    for ext in (".tar.gz", ".tar.zst", ".tar.bz2", ".tar.xz", ".tgz"):
        if name.endswith(ext):
            return ext.lstrip(".")
    suffix = path.suffix.lower().lstrip(".")
    return suffix or "unknown"


def format_handler_hint(path: Path) -> str:
    """Return which backend should parse the archive."""
    fmt = detect_format(path)
    if fmt == "7z":
        return "py7zr|libarchive"
    if fmt == "rar":
        return "unrar|libarchive"
    if fmt in {"iso", "dmg"}:
        return "libarchive|pycdlib"
    return "libarchive"
