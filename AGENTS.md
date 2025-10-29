# AGENTS.md

## Project Overview

Home Assistant AppDaemon applications for solar and HVAC energy optimization.

## Setup Commands

- Install dependencies: `uv sync`
- Run tests: `uv run pytest`
- Run linter: `uv run ruff check`
- Run type checker: `uv run pyright`
- Format code: `uv run ruff format`

## General rules

- Always ask if you are unsure what to do or if the potential impact of a change is large
- Comments: Use sparingly, explain WHY not WHAT

## Code Style

- Python 3.12+
- Line length: 120 characters
- Type hints required
- Follow ruff configuration in `pyproject.toml`
- Ensure consistency across codebase
- Protocol classes for Appdaemon dependency injection (see `apps/appdaemon_protocols/`)
- Callable protocols for strategy patterns (e.g., estimators, converters)
- Dataclasses with `frozen=True` for immutable data structures
- Include context in log messages (current values, thresholds, comparisons)
- Log warnings when optional data is missing but processing can continue
- Log errors only for genuine failures that prevent operation

## Testing Instructions

- Tests located in `tests/` directory
- Test files should follow `test_*.py` naming convention
- Keep tests in the same order as tested code
- Ensure consistency across tests
- Use pytest with `pythonpath = ["apps"]` configuration
- Mock dependencies using `unittest.mock.Mock`
- Define Shared fixtures in `conftest.py` for cross-module reuse
- Use fixtures to reduce test setup duplication
- Use `@pytest.mark.parametrize` to cover different scenarios
- Avoid redundant test cases
- Use dedicated tests for failure scenarios instead of mixing them with happy path cases
- Use `dataclasses.replace()` to create modified copies of frozen dataclasses in tests

## Architecture Patterns

- `apps/*_app.py` - AppDaemon integration layer that wires dependencies and handles framework interactions
- `apps/solar/` - Core solar related business logic isolated from the AppDaemon framework
  - `solar.py` - Main solar orchestration logic
  - `*_estimator.py` - Specialized estimators for energy usage and battery management decisions
  - `*_forecast.py` - Forecast data models and factories
  - `state.py` / `state_factory.py` - Home Assistant state management
- `apps/hvac/` - Core HVAC related business logic isolated from the AppDaemon framework
  - `hvac.py` - Main HVAC orchestration logic
  - `*_estimator.py` - Specialized estimators for DHW, heating and cooling temperatures
  - `state.py` / `state_factory.py` - Home Assistant state management
- `apps/units/` - Type-safe value objects for domain concepts (energy, power, SOC, etc.)
- `apps/utils/` - Shared utilities including safe type converters, battery converters/estimators, energy aggregators, and HVAC estimators
- `apps/appdaemon_protocols/` - Protocol interfaces for AppDaemon dependency injection and testability
