from __future__ import annotations

import fnmatch
from pathlib import PurePosixPath


def glob_match(pattern: str, path: str) -> bool:
    """Match archive entry paths against globs including ``**`` (F4.2)."""
    normalized = path.replace("\\", "/").lstrip("/")
    normalized_pattern = pattern.replace("\\", "/")

    if "**" in normalized_pattern:
        try:
            return PurePosixPath(normalized).match(normalized_pattern)
        except ValueError:
            pass
        if normalized_pattern in ("**/*", "**"):
            return bool(normalized)
        if normalized_pattern.startswith("**/"):
            suffix = normalized_pattern[3:]
            if suffix.startswith("*."):
                return normalized.endswith(suffix[1:])
            return normalized == suffix or normalized.endswith(f"/{suffix}")

    return fnmatch.fnmatch(normalized, normalized_pattern)
