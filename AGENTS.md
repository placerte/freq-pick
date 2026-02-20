# AGENTS.md

This file guides agentic coding assistants working in this repository.

## Repository Overview

- Project: `freq-pick`
- Language: Python
- Python version: 3.13 (from `pyproject.toml`)
- Package manager: `uv` (authoritative)
- Build backend: hatchling (authoritative)
- Current entry point: `main.py`
- Source tree: `src/` currently empty

## Authoritative Rules (carry into all work)

These are sourced from `docs/python_toolbox.md` and `docs/agent_executor_instructions_v_1.md`.

- Use `uv` for all installs and runs. Do not use `pip`, `venv`, or `conda`.
- Treat handoff documents as the only contract; do not invent requirements.
- If requirements are ambiguous, stop and report the blocker.
- Run required tests without asking permission when executing a handoff.
- Do not skip the Definition of Done; report failures and stop.
- Avoid reflection or string-based magic (`getattr`, `setattr`, dynamic wiring).
- Keep modules and functions small and conceptually focused.

## Cursor / Copilot Rules

- No `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md` found.

## Commands: Build / Lint / Test

The repository does not currently define tool configs in `pyproject.toml`.
Follow the toolbox defaults if tools are installed.

### Environment Setup

- Install dependencies: `uv sync`
- Add dependency: `uv add <package>`
- Add dev dependency: `uv add --dev <package>`

### Build

- Build package: `uv build`

### Format

- Format all code: `uv run black .`

### Type Check

- Run mypy: `uv run mypy .`

### Lint (optional, only if introduced)

- Run ruff: `uv run ruff check .`

### Test

- Run all tests: `uv run pytest`

### Test: Single File

- Run a file: `uv run pytest tests/test_example.py`

### Test: Single Test

- Run a test by node id:
  `uv run pytest tests/test_example.py::test_name`

### Test: By Keyword

- Run matching tests:
  `uv run pytest -k "keyword"`

## Code Style Guidelines

The project is minimal; follow the defaults below unless a handoff overrides them.

### Formatting

- Use Black defaults for formatting.
- Prefer explicit, readable code over clever expressions.
- Avoid dense comprehensions when a simple loop is clearer.

### Imports

- Standard library imports first, third-party next, local imports last.
- One import per line when it improves clarity.
- Avoid wildcard imports.
- Keep imports minimal and local to the module that uses them.

### Typing

- Type hints are required for new or modified public APIs.
- Avoid `Any` unless justified and localized.
- Prefer explicit types to dynamic behavior.
- Public dataclasses and functions should be fully typed.

### Naming

- Use `snake_case` for functions and variables.
- Use `PascalCase` for classes and dataclasses.
- Use `UPPER_CASE` for module constants.
- Name variables for intent, not type (`freq_hz`, not `arr1`).

### Error Handling

- Validate inputs early and raise `ValueError` for bad arguments.
- Prefer explicit exceptions over silent fallback.
- In CLI entry points, convert errors to non-zero exits.
- Do not swallow exceptions unless the caller explicitly needs it.

### Structure and Size

- Keep files focused by concept (core logic, UI, IO, CLI).
- Keep functions small and single-purpose.
- Avoid multi-responsibility "god" modules.

### Reflection / Magic

- Do not use reflection or string-based wiring.
- Avoid dynamic attribute access and `getattr`/`setattr`.
- Prefer explicit dependencies and direct method calls.

### Testing Conventions

- Tests live in `tests/`.
- Name test files `test_*.py`.
- Prefer small, deterministic tests with synthetic data.
- For matplotlib tests, use the Agg backend when headless.

## Project Layout (recommended by toolbox)

```text
project-root/
├── pyproject.toml
├── README.md
├── src/
│   └── freq_pick/
│       ├── __init__.py
│       ├── core.py
│       ├── mpl_ui.py
│       ├── artifacts.py
│       └── cli.py
├── tests/
│   └── test_*.py
└── docs/
```

## Notes for Agents

- Repository currently contains only `main.py` as a placeholder.
- No tests exist yet; create tests when adding new behavior.
- Keep dependency list minimal (the handoff allows numpy + matplotlib).
- Use `uv run <command>` for any execution.
