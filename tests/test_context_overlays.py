import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from freq_pick.core import OverlayContext
from freq_pick.core import Spectrum
from freq_pick.core import pick_freqs_matplotlib
from freq_pick.core import validate_context
from freq_pick.mpl_ui import PickerResult


def test_context_inputs_do_not_change_selection(monkeypatch) -> None:
    f_hz = np.linspace(0.0, 10.0, 11)
    mag = np.linspace(1.0, 2.0, 11)
    spectrum = Spectrum(f_hz=f_hz, mag=mag, display_domain="linear")

    def fake_run_picker(**_kwargs) -> PickerResult:
        fig = plt.figure()
        return PickerResult(selected_idx={2, 5}, cancelled=False, fig=fig)

    monkeypatch.setattr("freq_pick.mpl_ui.run_picker", fake_run_picker)

    selection_no_context = pick_freqs_matplotlib(spectrum)
    context = OverlayContext(mean=mag, p25=mag - 0.2, p75=mag + 0.2)
    selection_with_context = pick_freqs_matplotlib(spectrum, context=context)

    assert selection_no_context.selected_idx == selection_with_context.selected_idx


def test_context_missing_inputs_valid() -> None:
    f_hz = np.linspace(0.0, 10.0, 11)
    validate_context(f_hz, None)
    validate_context(f_hz, OverlayContext())


def test_context_length_mismatch_errors() -> None:
    f_hz = np.linspace(0.0, 10.0, 11)
    context = OverlayContext(mean=np.linspace(0.0, 1.0, 5))

    try:
        validate_context(f_hz, context)
    except ValueError as exc:
        assert "mean" in str(exc)
    else:
        raise AssertionError("Expected ValueError for mismatched overlay length.")
