from freq_pick.core import compose_title


def test_compose_title_with_append() -> None:
    assert compose_title("Base", "extra") == "Base extra"


def test_compose_title_without_append() -> None:
    assert compose_title("Base", None) == "Base"


def test_compose_title_without_base() -> None:
    assert compose_title(None, "extra") == "extra"


def test_compose_title_empty() -> None:
    assert compose_title(None, None) is None
