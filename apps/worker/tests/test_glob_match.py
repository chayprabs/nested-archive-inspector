from src.core.glob_match import glob_match


def test_double_star_so_suffix():
    assert glob_match("**/*.so", "payload/vendor/lib/plugin_00.so")
    assert not glob_match("**/*.so", "README")


def test_single_segment_glob():
    assert glob_match("*.txt", "readme.txt")
    assert not glob_match("*.txt", "nested/readme.txt")
