"""Generate a synthetic spectrum fixture (.npz)."""

from __future__ import annotations

from pathlib import Path

import numpy as np


def make_spectrum(
    *,
    f_min: float = 0.0,
    f_max: float = 200.0,
    df_hz: float = 0.5,
) -> tuple[np.ndarray, np.ndarray]:
    f_hz = np.arange(f_min, f_max + df_hz, df_hz)
    mag = 0.05 * np.random.default_rng(42).standard_normal(f_hz.size)

    peaks = [25.0, 60.0, 120.0, 175.0]
    for peak in peaks:
        mag += np.exp(-0.5 * ((f_hz - peak) / 1.5) ** 2) * 6.0

    return f_hz, mag


def main() -> None:
    out_dir = Path("artifacts")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "demo_spectrum.npz"

    f_hz, mag = make_spectrum()
    np.savez(out_path, f_hz=f_hz, mag=mag)
    print(f"Wrote fixture: {out_path}")


if __name__ == "__main__":
    main()
