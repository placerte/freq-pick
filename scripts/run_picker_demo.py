"""Launch the picker with a synthetic fixture."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from freq_pick.core import Spectrum
from freq_pick.core import pick_freqs_matplotlib


def main() -> None:
    fixture_path = Path("artifacts/demo_spectrum.npz")
    if not fixture_path.exists():
        raise SystemExit(
            "Fixture not found. Run: uv run python scripts/make_fixture.py"
        )

    with np.load(fixture_path) as data:
        f_hz = data["f_hz"]
        mag = data["mag"]

    spectrum = Spectrum(f_hz=f_hz, mag=mag, display_domain="dB")
    selection = pick_freqs_matplotlib(
        spectrum,
        user_snap_hz=0.5,
        artifact_dir=Path("artifacts"),
        artifact_stem="demo",
        xlim=(0.0, 200.0),
        title="Demo spectrum",
    )

    print("Selected indices:", selection.selected_idx)
    print("Selected frequencies:", selection.selected_hz)


if __name__ == "__main__":
    main()
