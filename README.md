# Home Assistant AppDaemon Applications

[![CI](https://github.com/mkuthan/home-assistant-appdaemon/actions/workflows/ci.yml/badge.svg)](https://github.com/mkuthan/home-assistant-appdaemon/actions/workflows/ci.yml)

[![codecov](https://codecov.io/gh/mkuthan/home-assistant-appdaemon/graph/badge.svg?token=OIJ3MV1L8G)](https://codecov.io/gh/mkuthan/home-assistant-appdaemon)

This project provides intelligent automation for solar-powered homes, optimizing energy usage and battery management to maximize self-consumption and minimize grid costs. By integrating real-time solar production data, household consumption patterns, weather forecasts, and dynamic electricity pricing, the system makes autonomous decisions about when to store, consume, or discharge battery energy.

## Features

- *Battery Reserve Management* - Dynamically adjusts battery reserve SOC to prevent grid import during high-tariff periods
- *Storage Mode Optimization* - Automatically determines the optimal hybrid inverter storage mode to maximize PV energy sales to the grid
- *Discharge Slot Optimization* - Calculates optimal battery discharge windows to maximize earnings from grid energy sales

## Architecture

The project follows a clean architecture pattern with clear separation of concerns:

- `apps/solar_app.py` - AppDaemon integration layer that wires dependencies and handles framework interactions
- `apps/solar/` - Core business logic isolated from the AppDaemon framework
  - `solar.py` - Main orchestration logic
  - `*_estimator.py` - Specialized estimators for energy usage and battery management decisions
  - `*_forecast.py` - Forecast data models and factories
  - `state.py` / `state_factory.py` - Home Assistant state management
- `apps/units/` - Type-safe value objects for domain concepts (energy, power, SOC, etc.)
- `apps/utils/` - Shared utilities and safe type converters
- `apps/appdaemon_protocols/` - Protocol interfaces for dependency injection and testability

## Design Principles

- *Dependency Injection* - Protocol classes enable testing without the AppDaemon runtime
- *Immutable Data* - Frozen dataclasses prevent accidental state mutations
- *Type Safety* - Full type hints enforced by ruff configuration
- *Testability* - Core logic is framework-agnostic and easily unit-testable

## Configuration

Applications are configured in `apps/apps.yaml`. See `apps/solar_app.py` for configuration options including:

- Battery capacity, voltage, and current limits
- SOC reserve thresholds and margins
- Heating system COP and thermal coefficients
- Fallback values for sensor failures

## References

- [Home Assistant solar automation prototype](https://mkuthan.github.io/blog/2025/04/12/home-assistant-solar/)
- [Solis Cloud Control integration](https://github.com/mkuthan/solis-cloud-control)
