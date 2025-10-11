# AGENTS.md

## Project Overview

Home Assistant AppDaemon applications for solar energy optimization.

## Setup Commands

- Install dependencies: `uv sync`
- Run tests: `uv run pytest`
- Run linter: `uv run ruff check`
- Format code: `uv run ruff format`

## Code Style

- Python 3.12+
- Use Protocol classes for Appdaemon dependency injection (see `apps/appdaemon_protocols/`)
- Dataclasses with `frozen=True` for immutable data structures
- Type hints required (enforced by ruff ANN rules)
- Line length: 120 characters
- Follow ruff configuration in `pyproject.toml`
- Comments: Use sparingly, explain WHY not WHAT


## Testing Instructions

- Tests located in `tests/` directory
- Use pytest with `pythonpath = ["apps"]` configuration
- Mock dependencies using `unittest.mock.Mock`
- Test files should follow `test_*.py` naming convention
- Run tests before committing: `uv run pytest`
- Use `@pytest.mark.parametrize` for parametrized tests to cover different scenarios
- Use separated test for failure scenarios

## Architecture Patterns

- Core business logic separated from AppDaemon framework (e.g., `Solar` class vs `SolarApp`)
- Static factory methods for data parsing with robust error handling
- BaseApp provides safe state converters and logging wrappers
