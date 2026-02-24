# Gotchas Log

> Purpose: Failure-pattern database.
> Style: Symptom → Diagnose → Fix → Prevention. Keep entries short and repo-agnostic.
> Tags: Use lowercase, bracketed tags like `[python][packaging][sdist]`. Prefer *mechanism* tags.

---

## Index

- **GOTCHA-001** — CLI exists but `import` fails — [python][packaging][sdist][entry-points][import]
- **GOTCHA-003** — Wheel installs but `import` fails — [python][packaging][wheel][hatchling][src-layout]
- **GOTCHA-002** — Frozen binary misses runtime import — [python][pyinstaller][packaging][hidden-import]

---

## Template (copy/paste)

```md
## GOTCHA-XXX — <short title>

**Tags:** [domain][mechanism][tooling][os]  
**Severity:** low|medium|high  
**Detectability:** low|medium|high  
**Last-seen:** YYYY-MM  

### Symptom
- <what you observe>

### Diagnose
```bash
# 1) <first command>
# 2) <second command>
# 3) <third command>
```

### Likely Cause
- <1–2 lines>

### Fix
- <bullet steps>

### Prevention
- <short checklist>

### Notes
- <optional, 1–3 bullets max>
```

---

## GOTCHA-001 — CLI exists but `import` fails

**Tags:** [python][packaging][sdist][entry-points][import]  
**Severity:** medium  
**Detectability:** high  
**Last-seen:** 2026-02  

### Symptom
- Console script exists in `.venv/bin/` (or `Scripts/` on Windows)
- But:
  - `ModuleNotFoundError: No module named '<import_name>'`
  - or `find_spec('<import_name>')` returns `None`

### Diagnose
Replace:
- `DIST_NAME` = distribution name (what pip installs)
- `IMPORT_NAME` = Python import name

```bash
uv run python -c "import importlib.metadata as m; print(m.version('DIST_NAME'))"
uv run python -c "import importlib.util as u; print(u.find_spec('IMPORT_NAME'))"
uv run python -c "import importlib.metadata as m; print(len(list(m.files('DIST_NAME') or [])))"
```

### Likely Cause
Broken or incomplete **sdist** (source distribution) missing `src/IMPORT_NAME/**`.

### Fix
- Ensure the build backend explicitly includes `src/IMPORT_NAME/**` in the **sdist**.
- Rebuild.
- Reinstall from the tarball in a clean venv.
- Verify `python -c "import IMPORT_NAME"`.

### Prevention
1. `uv build`
2. Inspect tarball contents
3. Install from tarball in a clean venv
4. `python -c "import IMPORT_NAME"`

### Notes
- Entry points live in distribution metadata; imports require the actual package files.
- A suspiciously small `files(...)` count often means only `.dist-info` landed in site-packages.

---

## GOTCHA-002 — Frozen binary misses runtime import

**Tags:** [python][pyinstaller][packaging][hidden-import]  
**Severity:** high  
**Detectability:** medium  
**Last-seen:** 2026-02  

### Symptom
- `uv run <cli>` works
- Frozen binary fails with `ModuleNotFoundError` for a dependency

### Diagnose
```bash
# 1) Confirm dependency is importable in the build venv
uv run python -c "import IMPORT_NAME; print(IMPORT_NAME.__file__)"

# 2) Check whether PyInstaller bundled it
uv run python -c "from PyInstaller.archive.readers import ZlibArchiveReader; z=ZlibArchiveReader('build/APP_NAME/PYZ-00.pyz'); print([n for n in z.toc if n.startswith('IMPORT_NAME')])"
```

### Likely Cause
- Dependency is imported only at runtime (inside a function), so PyInstaller cannot discover it.

### Fix
- Add to the `.spec`:
  - `from PyInstaller.utils.hooks import collect_submodules`
  - `hiddenimports += collect_submodules("IMPORT_NAME")`
- Rebuild: `uv run pyinstaller APP_NAME.spec`

### Prevention
- If an import is deferred or dynamic, declare it as a hidden import.
- Add a post-build check that asserts required modules exist in the PYZ.

---

## GOTCHA-003 — Wheel installs but `import` fails

**Tags:** [python][packaging][wheel][hatchling][src-layout]  \
**Severity:** medium  \
**Detectability:** high  \
**Last-seen:** 2026-02  \

### Symptom
- Wheel installs, CLI entry point exists
- But `import IMPORT_NAME` fails
- Wheel contains only `.dist-info` without `IMPORT_NAME/**`

### Diagnose
Replace:
- `WHEEL_PATH` = path to built wheel
- `IMPORT_NAME` = Python import name

```bash
uv run python -c "import zipfile; z=zipfile.ZipFile('WHEEL_PATH'); print([n for n in z.namelist() if n.startswith('IMPORT_NAME/')])"
```

### Likely Cause
- Hatchling wheel target mis-specified for `src/` layout, so packages are not included.

### Fix
- In `pyproject.toml`, set:
  - `[tool.hatch.build.targets.wheel]`
  - `packages = ["src/IMPORT_NAME"]`
- Rebuild and reinstall from the wheel.

### Prevention
1. `uv build`
2. Inspect wheel contents
3. Install in a clean venv
4. `python -c "import IMPORT_NAME"`

### Notes
- `sources = ["src"]` is not always enough for hatchling to find packages.
