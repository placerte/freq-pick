from freq_pick.core import toggle_index


def test_toggle_by_index() -> None:
    selected: set[int] = set()
    toggle_index(selected, 4)
    assert 4 in selected

    toggle_index(selected, 4)
    assert 4 not in selected
