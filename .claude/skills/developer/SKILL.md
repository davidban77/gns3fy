---
name: developer
description: Implement features following strict coding best practices with docs and tests
user-invocable: true
argument-hint: "<description of what to implement>"
---

# Developer Skill

Implement the requested feature or change following strict coding standards for gns3fy.

## Task

Implement: `$ARGUMENTS`

## Coding Standards (MANDATORY)

### Pydantic v1 (CRITICAL)
- Use `from pydantic.dataclasses import dataclass` and `from pydantic import validator`
- Use `Field(description="...", example=...)` for self-documenting model fields
- **NEVER** use Pydantic v2 APIs (`model_validator`, `model_config`, `ConfigDict`, etc.)
- Config class: `validate_assignment=True`, `extra="ignore"`

### Type Hints
- Use `typing` module: `Optional`, `Any`, `Dict`, `List`
- All function signatures must have complete type annotations

### Style
- Line length: 120 characters max
- PascalCase for classes, snake_case for functions/methods, UPPER_SNAKE_CASE for constants
- Private methods: single underscore prefix (`_create_session`)
- Formatter/linter: ruff (enforced in CI)

## Documentation (MANDATORY — No Exceptions)

### Every Function Must Have:
```python
def method_name(self, param: str) -> Optional[Dict]:
    """Short description of what it does.

    Args:
        param: Description of the parameter

    Raises:
        ValueError: When param is invalid

    Returns:
        Dictionary with response data, or None if not found
    """
```

### Every Class Must Have:
```python
@dataclass(config=Config)
class ClassName:
    """Short description of the class.

    Attributes:
        attr_name: Description of the attribute

    Examples:
        ```python
        obj = ClassName(connector=conn, attr_name="value")
        obj.get()
        ```
    """
```

### Inline Comments
- Add comments for non-obvious logic, API quirks, or workarounds
- Do NOT add comments that just restate the code

## Testing (First-Class Citizen)

- Aim for complete coverage of all new code paths
- Class-based tests following `TestClassName` pattern
- Use `requests-mock` for HTTP mocking
- JSON fixtures go in `tests/data/`
- Follow existing mock patterns (`Gns3ConnectorMock`, `Gns3ConnectorMockStopped`, etc.)
- Use the existing `post_put_matcher()` for dynamic POST/PUT responses

## Workflow

1. Read existing code to understand patterns and conventions
2. Implement the feature following all standards above
3. Write comprehensive tests
4. Run `task lint` — fix any issues
5. Run `task test-only` — ensure all tests pass
6. Update documentation if adding/changing public APIs:
   - README.md for new user-facing features
   - Docstrings for pydoc-markdown to pick up
