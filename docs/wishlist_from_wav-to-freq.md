# Wishlist from wav-to-freq

This wishlist is intentionally agnostic of wav-to-freq internals. The goal is
to make freq-pick's overlay feature explicit, discoverable, and robust for any
caller.

## API clarity

- Make `context: OverlayContext | None` the only supported overlay input in the
  picker API (no `**kwargs` fallbacks).
- Document the picker signature prominently in README/docs, with a minimal
  example that includes `context`.
- Keep the API agnostic of data origin (no project-specific naming or logic).

## Validation and errors

- Validate that all arrays in `OverlayContext` match the `f_ref` length and
  raise a clear error if any mismatch is detected.
- Provide a short, precise error message that identifies which field failed
  and the expected vs actual length.

## Helper constructor

- Add `OverlayContext.from_arrays(...)` (or similar) that:
  - accepts `mean`, `median`, `p25`, `p75`, `p10`, `p90`
  - validates shapes
  - returns a fully formed `OverlayContext`

## Diagnostics

- If `context` is provided but all arrays are `None`, log a warning or show a
  non-blocking message so callers can tell overlays were effectively empty.

## Tests

- Add tests that confirm:
  - overlays do not affect selected indices
  - invalid array lengths raise a clear error
  - a minimal `OverlayContext` (only one field set) still renders correctly
