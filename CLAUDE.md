# CLAUDE.md — AI Assistant Guide for gns3fy

## Project Overview

**gns3fy** is a Python wrapper library around the GNS3 Server REST API (v2). It provides programmatic interaction with GNS3 servers for network automation, CI/CD pipelines, and Ansible integration.

- **Language**: Python 3.6+
- **GNS3 Compatibility**: v2.2+
- **Package Manager**: Poetry
- **Current Version**: 0.7.2

## Repository Structure

```
gns3fy/                     # Main source package
├── __init__.py             # Exports: Gns3Connector, Project, Node, Link
├── gns3fy.py               # Core implementation (~2200 lines)
└── drawing_utils.py        # SVG drawing helper functions
tests/
├── test_gns3fy.py          # Main tests (~1600 lines)
├── test_drawing_utils.py   # Drawing utility tests
└── data/                   # JSON fixtures and mock data modules
docs/content/               # MkDocs documentation source
.github/workflows/tests.yml # CI pipeline
```

## Common Commands

```bash
# Install dependencies
poetry install --no-interaction

# Run full test suite (lint + format check + tests)
make test

# Individual commands
poetry run flake8 .                              # Lint
poetry run black --diff --check .                # Format check
poetry run pytest tests/ -v                      # Tests
poetry run pytest --cov-report=xml --cov=gns3fy tests  # Tests with coverage

# Documentation
make docs-generate   # Generate API reference from docstrings
make docs-show       # Serve docs locally
```

## Architecture & Key Classes

All core classes live in `gns3fy/gns3fy.py`:

- **`Gns3Connector`** — REST API client with HTTP session management, auth, and methods for all GNS3 resources
- **`Project`** — Pydantic dataclass for GNS3 projects; supports CRUD, nodes/links/drawings management
- **`Node`** — Pydantic dataclass for network nodes; supports start/stop/suspend/reload
- **`Link`** — Pydantic dataclass for network links between nodes
- **`Config`** — Internal Pydantic config: `validate_assignment=True`, `extra="ignore"`

Helper decorator `verify_connector_and_id()` validates that a connector and required IDs are set before API operations.

Constants: `NODE_TYPES` (14 types), `CONSOLE_TYPES` (8 types), `LINK_TYPES` (2 types).

## Code Conventions

- **Formatter**: Black (enforced in CI)
- **Linter**: Flake8 — max line length 120 (configured in `setup.cfg`)
- **Type Hints**: Use `typing` module (`Optional`, `Any`, `Dict`, `List`)
- **Data Models**: Pydantic dataclasses with `@dataclass(config=Config)`
- **Docstrings**: Markdown-formatted with embedded usage examples
- **Naming**: PascalCase for classes, UPPER_SNAKE_CASE for constants, snake_case for functions/methods
- **Private methods**: Single underscore prefix (`_create_session`)

## Testing

- **Framework**: pytest with class-based test structure
- **Mocking**: `requests-mock` adapter with custom mock classes:
  - `Gns3ConnectorMock` — base mock
  - `Gns3ConnectorMockStopped` — stopped node variant
  - `Gns3ConnectorMockSuspended` — suspended node variant
- **Fixtures**: JSON files in `tests/data/` (nodes.json, links.json, projects.json, templates.json, etc.)
- **Custom matcher**: `post_put_matcher()` for dynamic POST/PUT response handling
- **Coverage**: pytest-cov with Codecov integration

Test classes follow the pattern `TestGns3Connector`, `TestLink`, `TestNode`, `TestProject`.

## CI/CD

GitHub Actions (`.github/workflows/tests.yml`):
- Triggers on push and pull_request
- Matrix: Python 3.7, 3.8
- Steps: install Poetry 1.5.1 → cache deps → flake8 → black check → pytest with coverage → Codecov upload

## Dependencies

**Runtime**: `requests ^2.22`, `pydantic ^1.0`

**Dev**: `pytest ^5.0`, `flake8 ^3.7`, `requests-mock ^1.6`, `pytest-cov ^2.7`, `black`, `mkdocs ^1.0`, `mkdocs-material ^6.1.0`, `pydoc-markdown`

## Important Notes

- Always run `make test` (or the individual lint/format/test commands) before committing
- The library uses Pydantic v1 (`pydantic ^1.0`) — do not use Pydantic v2 APIs
- HTTP mocking in tests registers endpoints for GET/POST/PUT/DELETE across projects, nodes, links, templates, computes, snapshots, and drawings
- Documentation is auto-generated from docstrings via `pydoc-markdown` — keep docstrings up to date when modifying public APIs
