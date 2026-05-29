from pathlib import Path

from src.core.formats import detect_format, format_handler_hint


def test_detect_tar_gz():
    assert detect_format(Path("release-1.3.0.tar.gz")) == "tar.gz"


def test_rar_uses_unrar_hint():
    assert "unrar" in format_handler_hint(Path("sample.rar"))
