# Python Toolbox / Toolchain (Authoritative)

This document defines the **default Python tooling stack** and **coding rules** to be assumed by agents and humans when working on Python projects under this knowledge base.

It is intentionally boring, explicit, and reproducible.

---

## Scope

Applies to:
- local development
- agent execution environments
- CI-like execution (when applicable)

Unless a handoff explicitly overrides a choice, **this toolbox is the default**.

---

## Python Environment

- Python version: *project-defined* (explicit in `pyproject.toml` or README)
- Environment manager: **uv**

Rules:
- No `pip`, no `venv`, no `conda`
- All installs, builds, and runs go through `uv`

Typical commands:
- `uv init`
- `uv add <package>`
- `uv add --dev <package>`
- `uv run <command>`

---

## Packaging & Build System

- Build backend: **hatchling**
- Build frontend: **uv**

Rules:
- No setuptools unless explicitly justified
- No dynamic versioning unless required
- Prefer static metadata in `pyproject.toml`

Build commands:
- `uv build`
- `uv publish` (only when release is intentional)

Artifacts:
- Source distribution (sdist)
- Wheel

---

## Formatting & Style

- Formatter: **black**

Rules:
- No manual formatting debates
- Black defaults unless explicitly overridden
- Formatting is non-negotiable and automated

Typical usage:
- `uv run black .`

---

## Testing

- Test framework: **pytest**

Rules:
- Tests live in `tests/`
- Tests are executable via `uv run pytest`
- Failing tests block completion

Optional (when justified in handoff):
- markers for slow / integration tests

---

## Type Hints & Type Checking (Enforced)

Type hints are **required** for new code and maintained for edited code.

Rules:
- Public functions/methods: full type hints
- Public attributes: explicit types where practical
- Avoid `Any` unless justified (and localized)
- Prefer explicit, named types over clever typing tricks

Type checker:
- Tool: **mypy**
- Config must be explicit (e.g., `[tool.mypy]` in `pyproject.toml`)

Typical usage:
- `uv run mypy .`

---

## Linting (Minimal)

Linting is **minimal by default**.

If introduced, it must enforce *policy*, not style (Black already owns style).

Allowed (only if requested in a handoff):
- `ruff` (selected rules only)

Otherwise: skip linting.

---

## Coding Rules (Enforced)

These are *policy-level* constraints. Agents should treat them as hard rules unless a handoff explicitly overrides them.

### No reflection / no string-magic

Avoid:
- `getattr(obj, "name")`
- `setattr(...)`
- dynamic attribute fishing
- string-based wiring between components

Prefer:
- explicit attributes
- explicit method calls
- typed protocols / ABCs only when they genuinely simplify (avoid over-engineering)

### Keep code small and conceptually split

- Prefer smaller modules over large single files.
- Split by concept when it improves readability and testability.

### Keep functions small and single-purpose

- Avoid “do-everything” functions/methods.
- Split when a function:
  - becomes hard to name precisely
  - mixes parsing + business logic + IO
  - grows large enough that tests become awkward

---

## Project Layout (Recommended)

```text
project-root/
├── pyproject.toml
├── README.md
├── src/
│   └── package_name/
│       ├── __init__.py
│       ├── core.py
│       ├── models.py
│       └── ... (split by concept)
├── tests/
│   └── test_*.py
└── docs/ (optional)

