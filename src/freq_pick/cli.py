"""CLI entry point for freq-pick."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np

from freq_pick.core import OverlayContext
from freq_pick.core import PickerCancelled
from freq_pick.core import Spectrum
from freq_pick.core import pick_freqs_matplotlib


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pick frequencies from a spectrum.")
    parser.add_argument("--in", dest="input_path", required=True, type=Path)
    parser.add_argument("--out", dest="output_dir", required=True, type=Path)
    parser.add_argument("--stem", dest="stem", required=True)
    parser.add_argument("--snap-hz", dest="snap_hz", type=float, default=0.5)
    parser.add_argument(
        "--domain",
        dest="domain",
        choices=["linear", "dB"],
        default="dB",
        help="Display domain metadata only.",
    )
    parser.add_argument(
        "--xlim",
        dest="xlim",
        type=float,
        nargs=2,
        metavar=("FMIN", "FMAX"),
    )
    parser.add_argument("--title", dest="title", default=None)
    parser.add_argument("--title-append", dest="title_append", default=None)
    return parser.parse_args(argv)


def _load_npz(path: Path) -> tuple[np.ndarray, np.ndarray, OverlayContext | None]:
    if not path.exists():
        raise ValueError(f"Input file does not exist: {path}")
    with np.load(path) as data:
        if "f_hz" not in data or "mag" not in data:
            raise ValueError("Input .npz must contain f_hz and mag arrays.")
        overlays: dict[str, np.ndarray] = {}
        for key in ("mean", "median", "p25", "p75", "p10", "p90"):
            if key in data:
                overlays[key] = data[key]
        context = OverlayContext(**overlays) if overlays else None
        return data["f_hz"], data["mag"], context


def main(argv: list[str] | None = None) -> None:
    """CLI entry point. [S-260220_1-5]"""
    args = _parse_args(argv)
    try:
        f_hz, mag, context = _load_npz(args.input_path)
        spectrum = Spectrum(f_hz=f_hz, mag=mag, display_domain=args.domain)
        selection = pick_freqs_matplotlib(
            spectrum,
            user_snap_hz=args.snap_hz,
            artifact_dir=args.output_dir,
            artifact_stem=args.stem,
            xlim=tuple(args.xlim) if args.xlim is not None else None,
            title=args.title,
            title_append=args.title_append,
            context=context,
        )
        if selection.selected_idx:
            print(f"Selected {len(selection.selected_idx)} peaks.")
        else:
            print("No peaks selected.")
    except PickerCancelled:
        print("Picker cancelled.", file=sys.stderr)
        raise SystemExit(1)
    except Exception as exc:  # pragma: no cover - CLI guardrail
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
