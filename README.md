# freq-pick

Interactive frequency picker for a single spectrum. The API accepts a precomputed
frequency axis and magnitude array, launches a matplotlib UI, and returns a
deterministic list of selected bin indices and frequencies. Optional PNG/JSON
artifacts capture the selection.

## Install

```bash
uv add freq-pick
```

## API (primary)

Picker signature (overlay input is `context` only):

```python
pick_freqs_matplotlib(spectrum, *, context: OverlayContext | None = None, ...)
```

```python
from pathlib import Path
import numpy as np

from freq_pick.core import OverlayContext
from freq_pick.core import Spectrum
from freq_pick.core import pick_freqs_matplotlib

f_hz = np.linspace(0.0, 200.0, 1001)
mag = np.sin(f_hz / 10.0) ** 2

context = OverlayContext.from_arrays(
    f_hz,
    mean=mag,
)

spectrum = Spectrum(f_hz=f_hz, mag=mag, display_domain="linear")
selection = pick_freqs_matplotlib(
    spectrum,
    user_snap_hz=0.5,
    xlim=(0.0, 200.0),
    title="Demo",
    title_append="[1/5]",
    artifact_dir=Path("artifacts"),
    artifact_stem="demo",
    context=context,
)

print(selection.selected_idx)
print(selection.selected_hz)
```

### Controls

- `shift + drag` rectangle: select max magnitude in the rectangle
- `q`: commit and quit
- `Esc`: cancel
- `c`: clear selection
- `x`: delete nearest selected peak to cursor
- `l`: toggle y scale (linear/dB)
- `o`: toggle overlay context
- `h`: toggle help overlay

Overlays start visible when present and can be toggled on/off with `o`.

## CLI

```bash
uv run freq-pick \
  --in spectrum.npz \
  --out artifacts \
  --stem run1 \
  --snap-hz 0.5 \
  --domain dB \
  --xlim 0 200 \
  --title "Spec A" \
  --title-append "[3/10]"
```

Input `.npz` must include `f_hz` and `mag` arrays.
Optional context arrays (same length as `f_hz`) are loaded if present:

- `mean`, `median`
- `p25`, `p75`
- `p10`, `p90`

## Artifacts

When `artifact_dir` and `artifact_stem` are provided, the picker writes:

- `{stem}_pick.png`
- `{stem}_pick.json`

JSON keys:

- `schema_version`
- `selected_hz`
- `selected_idx`
- `settings`
- `spectrum_meta`
- `display_domain`
