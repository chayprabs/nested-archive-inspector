from src.core.flags import (
    blocked_extract,
    compression_ratio_flag,
    detect_path_traversal,
    detect_symlink_escape,
)
from src.models import ArchiveEntry


def test_path_traversal_detected():
    assert detect_path_traversal("../../etc/passwd")
    assert detect_path_traversal("/etc/passwd")
    assert not detect_path_traversal("safe/path.txt")


def test_symlink_escape_detected():
    assert detect_symlink_escape("link", "/etc/passwd")
    assert not detect_symlink_escape("link", "inner/file.txt")


def test_compression_ratio_flag():
    assert compression_ratio_flag(10_000, 1)
    assert not compression_ratio_flag(10, 10)


def test_blocked_extract_union():
    assert blocked_extract(["path_traversal"])
    assert not blocked_extract(["encrypted"])
