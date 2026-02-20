import numpy as np

from freq_pick.core import compute_df_hz
from freq_pick.core import effective_snap_hz
from freq_pick.core import snap_index


def test_snap_max_in_window() -> None:
    f_hz = np.arange(0.0, 10.0, 1.0)
    mag = np.array([0.0, 1.0, 2.0, 5.0, 1.0, 0.0, 1.0, 6.0, 2.0, 1.0])
    df_hz = compute_df_hz(f_hz)
    snap_hz = effective_snap_hz(0.5, df_hz)

    idx_left = snap_index(f_hz, mag, target_hz=2.2, window_hz=snap_hz)
    idx_right = snap_index(f_hz, mag, target_hz=7.2, window_hz=snap_hz)

    assert idx_left == 3
    assert idx_right == 7
