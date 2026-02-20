"""Artifact writing utilities."""

from __future__ import annotations

from pathlib import Path
import json

from matplotlib.figure import Figure

from freq_pick.core import Selection


def write_png(fig: Figure, path: Path) -> None:
    """Write PNG artifact. [S-260220_1-4]"""
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")


def write_selection_json(
    path: Path,
    selection: Selection,
    display_domain: str,
) -> None:
    """Write JSON artifact. [S-260220_1-6]"""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1",
        "selected_hz": selection.selected_hz,
        "selected_idx": selection.selected_idx,
        "settings": selection.settings,
        "spectrum_meta": selection.meta,
        "display_domain": display_domain,
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_artifacts(
    *,
    artifact_dir: Path,
    artifact_stem: str,
    fig: Figure,
    selection: Selection,
    display_domain: str,
) -> tuple[Path, Path]:
    """Write PNG + JSON artifacts. [D-260220_1-7]"""
    png_path = artifact_dir / f"{artifact_stem}_pick.png"
    json_path = artifact_dir / f"{artifact_stem}_pick.json"
    write_png(fig, png_path)
    write_selection_json(json_path, selection, display_domain)
    return png_path, json_path
