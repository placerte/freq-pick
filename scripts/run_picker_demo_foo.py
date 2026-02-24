"""Launch the picker with overlay context enabled."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from freq_pick.core import OverlayContext
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

    rng = np.random.default_rng(123)
    wiggle = 0.08 * np.sin(2.0 * np.pi * f_hz / 20.0) + 0.05 * np.sin(
        2.0 * np.pi * f_hz / 7.5
    )
    noise = 0.05 * rng.standard_normal(f_hz.size)

    mean = mag + wiggle + noise
    median = mag + 0.6 * wiggle - 0.5 * noise
    band_base = 0.25 + 0.05 * np.sin(2.0 * np.pi * f_hz / 30.0)
    band_noise = 0.1 * np.abs(noise)
    p25 = mag - band_base - band_noise
    p75 = mag + band_base + band_noise
    p10 = mag - 2.0 * band_base - 2.0 * band_noise
    p90 = mag + 2.0 * band_base + 2.0 * band_noise

    context = OverlayContext(
        mean=mean,
        median=median,
        p25=p25,
        p75=p75,
        p10=p10,
        p90=p90,
    )

    spectrum = Spectrum(f_hz=f_hz, mag=mag, display_domain="dB")
    selection = pick_freqs_matplotlib(
        spectrum,
        user_snap_hz=0.5,
        artifact_dir=Path("artifacts"),
        artifact_stem="demo_overlay",
        xlim=(0.0, 200.0),
        title="Demo spectrum (overlays)",
        context=context,
    )

    print("Selected indices:", selection.selected_idx)
    print("Selected frequencies:", selection.selected_hz)


if __name__ == "__main__":
    main()
