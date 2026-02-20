from freq_pick.cli import _parse_args


def test_cli_title_append_parses() -> None:
    args = _parse_args(
        [
            "--in",
            "demo.npz",
            "--out",
            "out",
            "--stem",
            "demo",
            "--title-append",
            "[1/5]",
        ]
    )

    assert args.title_append == "[1/5]"
