import json

from freq_pick.artifacts import write_selection_json
from freq_pick.core import Selection


def test_selection_json_schema(tmp_path) -> None:
    selection = Selection(
        selected_hz=[1.0, 2.0],
        selected_idx=[1, 2],
        settings={"user_snap_hz": 0.5},
        meta={"source": "test"},
    )
    path = tmp_path / "pick.json"
    write_selection_json(path, selection, display_domain="dB")

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    assert payload["schema_version"] == "1"
    assert payload["selected_hz"] == [1.0, 2.0]
    assert payload["selected_idx"] == [1, 2]
    assert "settings" in payload
    assert "spectrum_meta" in payload
    assert payload["display_domain"] == "dB"
