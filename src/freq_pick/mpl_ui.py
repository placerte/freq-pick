"""Matplotlib UI for interactive frequency picking."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from typing import cast

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.artist import Artist
from matplotlib.backend_bases import Event
from matplotlib.backend_bases import KeyEvent
from matplotlib.backend_bases import MouseButton
from matplotlib.backend_bases import MouseEvent
from matplotlib.figure import Figure
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.text import Text
from matplotlib.widgets import RectangleSelector

from freq_pick.core import OverlayContext
from freq_pick.core import toggle_index


@dataclass
class PickerResult:
    """UI result container. [S-260220_1-1]"""

    selected_idx: set[int]
    cancelled: bool
    fig: Figure


def _event_has_modifier(event_key: str | None, modifier: str) -> bool:
    if event_key is None:
        return False
    return modifier in event_key.split("+")


def _indices_in_view(
    selected_idx: Iterable[int],
    view_offset: int,
    view_size: int,
) -> list[int]:
    view_indices = []
    for idx in selected_idx:
        view_idx = idx - view_offset
        if 0 <= view_idx < view_size:
            view_indices.append(view_idx)
    return view_indices


def linear_to_db(linear_mag: np.ndarray, max_linear: float) -> np.ndarray:
    """Convert linear magnitudes to dB with a reference max."""
    if not np.isfinite(max_linear) or max_linear <= 0:
        max_linear = 1.0
    mag_safe = np.maximum(linear_mag, max_linear * 1e-12)
    return 20.0 * np.log10(mag_safe / max_linear)


def db_to_linear(db_mag: np.ndarray, max_linear: float = 1.0) -> np.ndarray:
    """Convert dB magnitudes to linear with a reference max."""
    if not np.isfinite(max_linear) or max_linear <= 0:
        max_linear = 1.0
    return max_linear * np.power(10.0, db_mag / 20.0)


def run_picker(
    *,
    f_hz: np.ndarray,
    mag: np.ndarray,
    display_domain: str,
    modifier: str,
    effective_snap_hz: float,
    title: str | None,
    xlim: tuple[float, float] | None,
    picker_keymap: dict[str, str],
    original_offset: int = 0,
    context: OverlayContext | None = None,
) -> PickerResult:
    """Matplotlib picker UI. [D-260220_1-6]"""
    fig, ax = plt.subplots()
    original_mag = mag
    current_domain = display_domain
    max_linear = float(np.max(original_mag)) if original_mag.size else 1.0
    if not np.isfinite(max_linear) or max_linear <= 0:
        max_linear = 1.0

    def convert_mag(values: np.ndarray, domain: str) -> np.ndarray:
        if domain == "linear":
            if display_domain == "linear":
                return values
            return db_to_linear(values, max_linear=1.0)
        if display_domain == "linear":
            return linear_to_db(values, max_linear=max_linear)
        return values

    def display_mag_for(domain: str) -> np.ndarray:
        return convert_mag(original_mag, domain)

    current_mag = display_mag_for(current_domain)
    (spectrum_line,) = ax.plot(f_hz, current_mag, color="black", linewidth=1.0)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel(f"Magnitude ({current_domain})")
    if title:
        ax.set_title(title)
    if xlim is not None:
        ax.set_xlim(xlim)

    selected_idx: set[int] = set()
    line_artists: list[Line2D] = []
    label_artists: list[Text] = []
    context_artists: list[Artist] = []
    legend_artist: Legend | None = None

    overlay_context = context if context is not None else OverlayContext()
    overlays_enabled = overlay_context.has_any()
    overlays_visible = overlays_enabled

    help_lines = [
        f"{modifier}+drag: toggle max in rectangle",
        f"{picker_keymap['commit']}: commit and quit",
        f"{picker_keymap['cancel']}: cancel",
        f"{picker_keymap['clear']}: clear",
        f"{picker_keymap['delete_nearest']}: delete nearest",
        f"{picker_keymap['toggle_scale']}: toggle y scale",
        f"{picker_keymap['toggle_overlays']}: toggle overlays",
        f"{picker_keymap['help']}: toggle help",
    ]
    help_text = ax.text(
        0.02,
        0.98,
        "\n".join(help_lines),
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=9,
        bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "black"},
        visible=False,
    )

    keymap_text = ax.text(
        0.98,
        0.02,
        f"{picker_keymap['help']} help",
        transform=ax.transAxes,
        va="bottom",
        ha="right",
        fontsize=9,
        bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "black"},
    )

    summary_text = ax.text(
        0.98,
        0.98,
        "",
        transform=ax.transAxes,
        va="top",
        ha="right",
        fontsize=9,
        bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "black"},
    )

    state = {
        "done": False,
        "cancelled": False,
        "last_mouse_x": None,
    }

    def update_selection_overlays() -> None:
        for artist in line_artists:
            artist.remove()
        for artist in label_artists:
            artist.remove()

        line_artists.clear()
        label_artists.clear()

        view_indices = _indices_in_view(selected_idx, original_offset, f_hz.size)
        view_indices.sort(key=lambda idx: f_hz[idx])

        y_min, y_max = ax.get_ylim()
        y_label = y_max - 0.02 * (y_max - y_min)
        for view_idx in view_indices:
            freq = float(f_hz[view_idx])
            line = ax.axvline(freq, color="tab:red", linewidth=1.2)
            label = ax.text(
                freq,
                y_label,
                f"{freq:.2f} Hz",
                rotation=90,
                va="top",
                ha="right",
                fontsize=8,
                color="tab:red",
            )
            line_artists.append(line)
            label_artists.append(label)

        summary_freqs = [float(f_hz[idx]) for idx in view_indices]
        summary_text.set_text("\n".join(f"{freq:.2f} Hz" for freq in summary_freqs))

        fig.canvas.draw_idle()

    def update_context_overlays() -> None:
        nonlocal legend_artist
        for artist in context_artists:
            artist.remove()
        context_artists.clear()
        if legend_artist is not None:
            legend_artist.remove()
            legend_artist = None

        if not overlays_enabled or not overlays_visible:
            fig.canvas.draw_idle()
            return

        legend_handles: list[Artist] = []
        legend_labels: list[str] = []

        def add_line(values: np.ndarray | None, color: str, label: str) -> None:
            if values is None:
                return
            display_values = convert_mag(values, current_domain)
            (line,) = ax.plot(
                f_hz,
                display_values,
                color=color,
                linewidth=1.1,
                alpha=0.9,
                label=label,
            )
            context_artists.append(line)
            legend_handles.append(line)
            legend_labels.append(label)

        def add_band(
            low: np.ndarray | None,
            high: np.ndarray | None,
            color: str,
            alpha: float,
            label: str,
        ) -> None:
            if low is None or high is None:
                return
            low_display = convert_mag(low, current_domain)
            high_display = convert_mag(high, current_domain)
            band = ax.fill_between(
                f_hz,
                low_display,
                high_display,
                color=color,
                alpha=alpha,
                linewidth=0.0,
            )
            context_artists.append(band)
            legend_handles.append(band)
            legend_labels.append(label)

        add_band(
            overlay_context.p10,
            overlay_context.p90,
            color="tab:gray",
            alpha=0.12,
            label="p10-p90",
        )
        add_band(
            overlay_context.p25,
            overlay_context.p75,
            color="tab:blue",
            alpha=0.18,
            label="p25-p75",
        )
        add_line(overlay_context.mean, color="tab:blue", label="mean")
        add_line(overlay_context.median, color="tab:orange", label="median")

        if legend_handles:
            legend_artist = ax.legend(
                handles=legend_handles,
                labels=legend_labels,
                loc="lower left",
                bbox_to_anchor=(0.01, 0.01),
                framealpha=0.9,
                facecolor="white",
                edgecolor="black",
                fontsize=9,
            )
            legend_artist.set_zorder(10)

        fig.canvas.draw_idle()

    def toggle_selected(view_idx: int) -> None:
        original_idx = view_idx + original_offset
        toggle_index(selected_idx, original_idx)
        update_selection_overlays()

    def on_select(eclick: MouseEvent, erelease: MouseEvent) -> None:
        """Rectangle select max-in-rectangle. [S-260220_1-2]"""
        if not (
            _event_has_modifier(eclick.key, modifier)
            or _event_has_modifier(erelease.key, modifier)
        ):
            return
        if eclick.xdata is None or eclick.ydata is None:
            return
        if erelease.xdata is None or erelease.ydata is None:
            return

        x0, x1 = sorted([eclick.xdata, erelease.xdata])
        y0, y1 = sorted([eclick.ydata, erelease.ydata])
        x_mask = (f_hz >= x0) & (f_hz <= x1)
        y_mask = (current_mag >= y0) & (current_mag <= y1)
        mask = x_mask & y_mask
        if not np.any(mask):
            return

        indices = np.where(mask)[0]
        local_mag = current_mag[indices]
        view_idx = int(indices[int(np.argmax(local_mag))])
        toggle_selected(view_idx)

    def on_motion(event: object) -> None:
        mouse_event = cast(MouseEvent, event)
        if mouse_event.inaxes != ax:
            return
        state["last_mouse_x"] = mouse_event.xdata

    def on_key_press(event: object) -> None:
        nonlocal current_domain, current_mag, overlays_visible
        key_event = cast(KeyEvent, event)
        if key_event.key == picker_keymap["commit"]:
            state["done"] = True
            plt.close(fig)
            return
        if key_event.key == picker_keymap["cancel"]:
            state["cancelled"] = True
            plt.close(fig)
            return
        if key_event.key == picker_keymap["clear"]:
            selected_idx.clear()
            update_selection_overlays()
            return
        if key_event.key == picker_keymap["delete_nearest"]:
            if not selected_idx:
                return
            target = state["last_mouse_x"]
            if target is None:
                return
            view_indices = _indices_in_view(selected_idx, original_offset, f_hz.size)
            if not view_indices:
                return
            nearest_view = min(view_indices, key=lambda idx: abs(f_hz[idx] - target))
            toggle_selected(nearest_view)
            return
        if key_event.key == picker_keymap["help"]:
            help_text.set_visible(not help_text.get_visible())
            fig.canvas.draw_idle()
            return
        if key_event.key == picker_keymap["toggle_scale"]:
            current_domain = "linear" if current_domain == "dB" else "dB"
            current_mag = display_mag_for(current_domain)
            spectrum_line.set_ydata(current_mag)
            ax.relim()
            ax.autoscale_view()
            ax.set_ylabel(f"Magnitude ({current_domain})")
            update_selection_overlays()
            update_context_overlays()
            return
        if key_event.key == picker_keymap["toggle_overlays"]:
            if overlays_enabled:
                overlays_visible = not overlays_visible
                update_context_overlays()
            return

    selector = RectangleSelector(
        ax,
        on_select,
        useblit=False,
        button=[MouseButton.LEFT],
        spancoords="data",
        interactive=False,
        props={"facecolor": "tab:blue", "alpha": 0.15, "edgecolor": "tab:blue"},
    )
    state["selector"] = selector

    fig.canvas.mpl_connect("motion_notify_event", on_motion)
    fig.canvas.mpl_connect("key_press_event", on_key_press)

    update_selection_overlays()
    update_context_overlays()
    plt.show(block=True)

    return PickerResult(
        selected_idx=selected_idx, cancelled=state["cancelled"], fig=fig
    )
