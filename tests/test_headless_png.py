import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from freq_pick.artifacts import write_png


def test_headless_png_write(tmp_path) -> None:
    fig, ax = plt.subplots()
    ax.plot([0.0, 1.0, 2.0], [0.0, 1.0, 0.5])

    path = tmp_path / "plot.png"
    write_png(fig, path)

    assert path.exists()
    assert path.stat().st_size > 0
