---
name: code-reviewer
description: Review code changes for best practices, complexity, compatibility, and gaps
user-invocable: true
argument-hint: "[git ref range or 'staged', defaults to develop..HEAD]"
context: fork
agent: general-purpose
allowed-tools: Read, Bash, Grep, Glob
---

# Code Reviewer Skill

Perform a read-only review of code changes for best practices compliance, complexity, compatibility, and gaps.

## Target

Review changes in: `$ARGUMENTS` (default: `develop..HEAD`)

If `$ARGUMENTS` is `staged`, review `git diff --cached` instead.

## Review Checklist

### 1. Best Practices Compliance

Check against the project's `/developer` standards:

- [ ] Docstrings with `Args:`, `Raises:`, `Returns:` on all new/modified functions
- [ ] Pydantic `Field(description=...)` usage on new model fields
- [ ] Complete type hints on all function signatures
- [ ] Tests written for new functionality
- [ ] Documentation updated for user-facing changes

### 2. Complexity Flags

Flag any of these patterns:

- Functions longer than 30 lines
- Nesting deeper than 3 levels
- Functions with more than 5 parameters
- Overly complex conditional logic

### 3. Compatibility Checks

Verify compliance with project constraints:

- Python 3.9+ compatibility (no walrus operator in critical paths, no `match` statements)
- Pydantic v1 API only (no `model_validator`, `model_config`, `ConfigDict`)
- No new dependencies added without justification
- `requests` library patterns (no `httpx`, `aiohttp` unless justified)

### 4. Gap Analysis

Identify missing pieces:

- Missing error handling for API calls (HTTP errors, timeouts, connection errors)
- Missing edge case tests (empty responses, malformed data, error codes)
- Missing docs for user-facing changes
- Missing validation on user inputs

## Output Format

Produce a structured review with three severity levels:

### Blockers
Must be fixed before merging. Include file path, line number, and clear description.

### Warnings
Should be addressed but not blocking. Include file path, line number, and suggestion.

### Suggestions
Nice-to-have improvements. Include file path and brief description.

## Rules

- **DO NOT modify any files** — this is a read-only review
- Read the actual diff/changed files to give specific, line-level feedback
- Consider the full context of each change, not just the diff
- Be constructive — suggest fixes, not just problems
