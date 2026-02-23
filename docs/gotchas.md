# gotchas.md
# Packaging gotchas: “console script exists but import fails”
# (for agents working on Python packaging + uv + hatchling)

## Symptom pattern
- A console script exists in `.venv/bin` (e.g., `freq-pick`)
- But Python cannot import the module (e.g., `ModuleNotFoundError: No module named 'freq_pick'`)

## Quick diagnostics (copy/paste)
### 1) Are we using the expected interpreter / env?
uv run python -c "import sys; print(sys.executable); print(sys.prefix)"

### 2) Is the distribution installed (metadata), even if the module is missing?
uv run python -c "import importlib.metadata as m; print(m.version('freq-pick')); print(len(list(m.files('freq-pick') or [])))"

### 3) Does the module exist?
uv run python -c "import importlib.util as u; print(u.find_spec('freq_pick'))"

Interpretation:
- If `m.version(...)` works but `find_spec(...)` is None:
  => The dist is installed, but the package files are not present in site-packages.
- If `dist files count` is very small (~10–30):
  => often only `.dist-info` got installed; code was missing from build artifact.

## Root cause (common)
Wheel configuration does NOT automatically ensure the SDist includes package sources.
- It’s possible to build/upload a wheel that contains `src/<pkg>/...`
- while the sdist tarball accidentally omits `src/<pkg>/...`

If downstream installs from sdist (or a direct `.tar.gz` URL), the install can succeed
(metadata + entry points), but the package module won’t exist.

## “Why is there a CLI but no module?”
Console scripts are generated from dist metadata (entry points).
If the module files are missing, the script still gets created, but it crashes at runtime.

## Specific gotcha: dependencies pinned to a tarball URL
If a downstream project depends on:
- `pkg @ https://files.pythonhosted.org/.../pkg-x.y.z.tar.gz`

…then it’s explicitly sourcing from the sdist artifact.
If that sdist is incomplete, imports will fail even if wheel settings look correct.

## Corrective actions (hatchling + src layout)
Add explicit SDist include rules:

[tool.hatch.build.targets.sdist]
include = [
  "src/<package_name>/**",
  "pyproject.toml",
  "README.md",
  "LICENSE",
]

Keep wheel config as needed:

[tool.hatch.build.targets.wheel]
packages = ["<package_name>"]
sources = ["src"]

## Pre-publish verification checklist
Build:
- uv build

Inspect SDist contents:
- tar -tf dist/<name>-<ver>.tar.gz | rg "^src/<package_name>/"

Smoke-test install from SDist (in a clean env):
- python -m venv /tmp/testenv && source /tmp/testenv/bin/activate
- pip install dist/<name>-<ver>.tar.gz
- python -c "import <package_name>; import <package_name>.<submodule>; print('ok')"

## Workarounds (when you need it working immediately)
- Use an editable install from local checkout:
  uv add --editable ../<repo>
- Or use a Git dependency:
  uv add "<name> @ git+https://github.com/<org>/<repo>.git@<tag>"

