"""Core API for selecting frequencies from a spectrum."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal
import warnings

import numpy as np

DISPLAY_DOMAINS: tuple[str, str] = ("linear", "dB")
PICKER_KEYMAP = {
    "commit": "q",
    "cancel": "escape",
    "clear": "c",
    "help": "h",
    "delete_nearest": "x",
    "toggle_scale": "l",
}


def compose_title(title: str | None, title_append: str | None) -> str | None:
    """Compose a plot title with optional appended text."""
    if title is None:
        return title_append
    if title_append is None:
        return title
    return f"{title} {title_append}"


_DF_WARN_REL_TOL = 1e-3
_DF_WARN_ABS_TOL = 1e-6


class PickerCancelled(Exception):
    """Raised when the user cancels the picker UI."""


@dataclass
class Spectrum:
    """Spectrum inputs for the picker. [D-260220_1-3]

    Args:
        f_hz: 1D array of strictly increasing frequencies (Hz).
        mag: 1D array of magnitudes aligned with f_hz.
        display_domain: "linear" or "dB" (no conversion is done in core).
        meta: Optional metadata copied into selection artifacts.
    """

    f_hz: np.ndarray
    mag: np.ndarray
    display_domain: Literal["linear", "dB"] = "dB"
    meta: dict[str, object] | None = None

    def __post_init__(self) -> None:
        validate_spectrum(self)


@dataclass
class Selection:
    """Picker output data. [D-260220_1-4]

    Attributes:
        selected_hz: Selected bin frequencies (raw bin values).
        selected_idx: Selected indices into the original spectrum arrays.
        settings: Picker settings used for the run.
        meta: Metadata copied from Spectrum.meta.
    """

    selected_hz: list[float]
    selected_idx: list[int]
    settings: dict[str, object]
    meta: dict[str, object]


def validate_spectrum(spectrum: Spectrum) -> None:
    """Validate spectrum inputs. [I-260220_1-2]

    Raises:
        ValueError: If any input constraint is violated.
    """
    if spectrum.display_domain not in DISPLAY_DOMAINS:
        raise ValueError("display_domain must be 'linear' or 'dB'.")

    if not isinstance(spectrum.f_hz, np.ndarray):
        raise ValueError("f_hz must be a numpy.ndarray.")
    if not isinstance(spectrum.mag, np.ndarray):
        raise ValueError("mag must be a numpy.ndarray.")

    if spectrum.f_hz.ndim != 1 or spectrum.mag.ndim != 1:
        raise ValueError("f_hz and mag must be 1D arrays.")
    if spectrum.f_hz.size == 0:
        raise ValueError("f_hz and mag must be non-empty.")
    if spectrum.f_hz.size != spectrum.mag.size:
        raise ValueError("f_hz and mag must be the same length.")

    if not np.all(np.isfinite(spectrum.f_hz)):
        raise ValueError("f_hz must contain only finite values.")
    if not np.all(np.isfinite(spectrum.mag)):
        raise ValueError("mag must contain only finite values.")

    diffs = np.diff(spectrum.f_hz)
    if not np.all(diffs > 0):
        raise ValueError("f_hz must be strictly increasing.")


def compute_df_hz(f_hz: np.ndarray) -> float:
    """Compute df_hz from spectrum bins. [I-260220_1-3]

    Returns:
        Median spacing of f_hz.
    """
    diffs = np.diff(f_hz)
    if diffs.size == 0:
        raise ValueError("Cannot compute df_hz from a single sample.")
    median_df = float(np.median(diffs))
    if median_df <= 0:
        raise ValueError("Computed df_hz must be positive.")

    max_dev = float(np.max(np.abs(diffs - median_df)))
    if max_dev > max(_DF_WARN_ABS_TOL, _DF_WARN_REL_TOL * median_df):
        warnings.warn(
            "f_hz spacing is non-uniform; df_hz is computed as the median.",
            UserWarning,
            stacklevel=2,
        )

    return median_df


def effective_snap_hz(user_snap_hz: float, df_hz: float) -> float:
    """Hybrid snap window definition. [D-260220_1-5]"""
    if user_snap_hz <= 0:
        raise ValueError("user_snap_hz must be positive.")
    return max(user_snap_hz, 3.0 * df_hz)


def snap_index(
    f_hz: np.ndarray,
    mag: np.ndarray,
    target_hz: float,
    window_hz: float,
) -> int:
    """Return the max-magnitude index within a window. [D-260220_1-5]

    The window is centered on target_hz and spans +/- window_hz.
    """
    if window_hz <= 0:
        raise ValueError("window_hz must be positive.")

    low = target_hz - window_hz
    high = target_hz + window_hz
    idx_lo = int(np.searchsorted(f_hz, low, side="left"))
    idx_hi = int(np.searchsorted(f_hz, high, side="right"))

    if idx_lo == idx_hi:
        return int(np.argmin(np.abs(f_hz - target_hz)))

    window_mag = mag[idx_lo:idx_hi]
    return int(np.argmax(window_mag) + idx_lo)


def toggle_index(selected_idx: set[int], index: int) -> None:
    """Toggle selection by index. [S-260220_1-3]"""
    if index in selected_idx:
        selected_idx.remove(index)
    else:
        selected_idx.add(index)


def crop_to_window(
    f_hz: np.ndarray,
    mag: np.ndarray,
    xlim: tuple[float, float],
) -> tuple[np.ndarray, np.ndarray, int]:
    """Crop spectrum to xlim window. [D-260220_1-8.1]"""
    fmin, fmax = xlim
    if fmin >= fmax:
        raise ValueError("xlim must be (min, max) with min < max.")

    idx_lo = int(np.searchsorted(f_hz, fmin, side="left"))
    idx_hi = int(np.searchsorted(f_hz, fmax, side="right"))
    if idx_lo == idx_hi:
        raise ValueError("xlim does not include any spectrum samples.")

    return f_hz[idx_lo:idx_hi], mag[idx_lo:idx_hi], idx_lo


def _build_selection(
    spectrum: Spectrum,
    selected_idx: set[int],
    settings: dict[str, object],
) -> Selection:
    """Build Selection output. [S-260220_1-1]"""
    sorted_idx = sorted(selected_idx, key=lambda idx: spectrum.f_hz[idx])
    selected_hz = [float(spectrum.f_hz[idx]) for idx in sorted_idx]
    meta = dict(spectrum.meta) if spectrum.meta is not None else {}
    return Selection(
        selected_hz=selected_hz,
        selected_idx=sorted_idx,
        settings=settings,
        meta=meta,
    )


def pick_freqs_matplotlib(
    spectrum: Spectrum,
    *,
    user_snap_hz: float = 0.5,
    modifier: str = "shift",
    artifact_dir: Path | None = None,
    artifact_stem: str | None = None,
    xlim: tuple[float, float] | None = None,
    title: str | None = None,
    title_append: str | None = None,
    crop_to_xlim: bool = True,
) -> Selection:
    """Launch matplotlib picker and return a Selection. [S-260220_1-1]

    Args:
        spectrum: Input Spectrum.
        user_snap_hz: Minimum snap window in Hz.
        modifier: Modifier key name ("shift").
        artifact_dir: Directory for PNG/JSON artifacts (optional).
        artifact_stem: Stem for artifact filenames (optional).
        xlim: Frequency window for display/cropping (optional).
        title: Base plot title (optional).
        title_append: Text appended to title (optional).
        crop_to_xlim: If true, selection is limited to xlim window.

    Raises:
        PickerCancelled: If the user cancels the UI.
        ValueError: For invalid inputs.
    """
    if artifact_dir is not None and artifact_stem is None:
        raise ValueError("artifact_stem must be provided with artifact_dir.")
    if artifact_stem is not None and artifact_dir is None:
        raise ValueError("artifact_dir must be provided with artifact_stem.")
    if user_snap_hz <= 0:
        raise ValueError("user_snap_hz must be positive.")

    df_hz = compute_df_hz(spectrum.f_hz)
    snap_hz = effective_snap_hz(user_snap_hz, df_hz)

    if xlim is not None and crop_to_xlim:
        f_view, mag_view, offset = crop_to_window(spectrum.f_hz, spectrum.mag, xlim)
    else:
        f_view, mag_view, offset = spectrum.f_hz, spectrum.mag, 0

    settings: dict[str, object] = {
        "user_snap_hz": user_snap_hz,
        "effective_snap_hz": snap_hz,
        "df_hz": df_hz,
        "modifier": modifier,
        "picker_keymap": dict(PICKER_KEYMAP),
    }
    if xlim is not None:
        settings["xlim"] = tuple(float(value) for value in xlim)
    if crop_to_xlim:
        settings["crop_to_xlim"] = True

    from freq_pick import artifacts
    from freq_pick import mpl_ui

    composed_title = compose_title(title, title_append)
    result = mpl_ui.run_picker(
        f_hz=f_view,
        mag=mag_view,
        display_domain=spectrum.display_domain,
        modifier=modifier,
        effective_snap_hz=snap_hz,
        title=composed_title,
        xlim=xlim,
        picker_keymap=PICKER_KEYMAP,
        original_offset=offset,
    )

    if result.cancelled:
        raise PickerCancelled("Picker cancelled by user.")

    if not result.selected_idx:
        warnings.warn("No peaks selected.", UserWarning, stacklevel=2)

    selection = _build_selection(spectrum, result.selected_idx, settings)

    if artifact_dir is not None and artifact_stem is not None:
        artifacts.write_artifacts(
            artifact_dir=artifact_dir,
            artifact_stem=artifact_stem,
            fig=result.fig,
            selection=selection,
            display_domain=spectrum.display_domain,
        )

    return selection
