import numpy as np

from freq_pick.mpl_ui import db_to_linear
from freq_pick.mpl_ui import linear_to_db


def test_linear_to_db_normalizes_to_max() -> None:
    linear = np.array([0.5, 1.0, 2.0])
    db = linear_to_db(linear, max_linear=2.0)
    assert np.isclose(db[-1], 0.0)


def test_db_to_linear_with_unit_max() -> None:
    db = np.array([0.0, -6.0])
    linear = db_to_linear(db, max_linear=1.0)
    assert np.isclose(linear[0], 1.0)
    assert np.isclose(linear[1], np.power(10.0, -6.0 / 20.0))
