# handoff-260224-1-freq-pick.md

Status: Execution Spec  
Date: 2026-02-24  
Repo: freq-pick  
Scope: Picker overlay inputs (context-only) + CLI/API agnosticism

---

# 1. Intent

Enhance the freq picker UI so that, while the user is picking frequencies on a single “signal at study”, they can optionally see additional contextual curves/bands (mean/median/percentile bands) for quality assessment.

Critical: freq-pick must remain **manual-authority**: overlays are informational only and must not influence picks except visually.

freq-pick is a standalone package with **CLI + API** entry points and must remain agnostic to upstream callers and data sources.

---

# 2. Core Principles (Non-Negotiable)

## P-260224-1 — Manual Authority

Nothing generates or edits FOIs except explicit user selection.

No auto-peak detection may create, alter, or remove picks.

---

## P-260224-2 — Overlays Are Informational Only

Overlay curves/bands may be displayed but:

- cannot be selected
- cannot become the “picking target”
- cannot affect snapping or indexing

---

# 3. Data Model & Inputs

## S-260224-1 — Minimal Input

freq-pick shall work with **only one input signal**:

- `signal_at_study`: y-values on a frequency grid
- `f_ref`: x-axis frequency grid (shared bins)

No overlays required.

---

## S-260224-2 — Optional Context Inputs

freq-pick shall accept optional overlays and bands, normalized to the same `f_ref` grid:

Optional overlay series (each same length as `f_ref`):

- `mean`
- `median`

Optional bands (each defined by two same-length arrays):

- `p25`, `p75`
- `p10`, `p90`

All optional inputs are strictly display-only.

---

## S-260224-3 — Normalization & Validation

- All provided arrays must align 1:1 with `f_ref`.
- If optional arrays are missing, picker still functions.
- If any optional array length mismatches `f_ref`, raise a clear error (API) / show a clear message (CLI) and exit non-zero.

---

# 4. Picker UI Behavior

## S-260224-4 — Picking Target

The active picking target remains:

    signal_at_study

Selection must map to bin indices of `f_ref`.

No overlay curve or band may be selectable.

---

## S-260224-5 — Overlay Toggle

Overlays/bands must be toggleable at runtime via a keybinding.

Default state:

- overlays OFF (conservative) OR remember last state (acceptable)

Either is acceptable, but the behavior must be deterministic and documented.

---

# 5. API Contract

## I-260224-1

- Extend the picker API to accept optional overlays/bands as inputs.
- Ensure return value (picked bin indices) is unchanged and remains independent of overlays.
- Provide clear typing/docs: “only `signal_at_study` is pickable”.

---

# 6. CLI Contract

## I-260224-2

- CLI shall accept:
  - mandatory input for `signal_at_study` (+ its `f_ref`)
  - optional inputs for overlays/bands
- CLI must remain agnostic of data origin (no wav-to-freq specifics baked in).

---

# 7. Definition of Done

## DoD-260224-1

- With only `signal_at_study` provided, the picker works exactly as before.
- With overlays provided, the user can toggle them.
- Picks (bin indices) are identical regardless of overlay visibility.
- Overlays cannot be selected and do not affect snapping.

---

# 8. Tests

## T-260224-1

Overlay visibility does not change selected bin indices.

## T-260224-2

Missing overlays/bands does not change functionality.

## T-260224-3

Mismatched-length overlay input produces a clear error.

---

End of handoff-260224-1-freq-pick.md

