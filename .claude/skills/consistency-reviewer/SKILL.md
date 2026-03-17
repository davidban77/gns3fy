---
name: consistency-reviewer
description: Review codebase for CLEAN code practices and DRY violations
user-invocable: true
argument-hint: "[file or directory to review, defaults to gns3fy/]"
context: fork
agent: general-purpose
allowed-tools: Read, Bash, Grep, Glob
---

# Consistency Reviewer Skill

Perform a read-only review of the codebase for CLEAN code practices and DRY violations.

## Target

Review: `$ARGUMENTS` (default: `gns3fy/`)

## CLEAN Code Checklist

Evaluate each principle and report findings:

- **C**ohesion: Does each function/class have a single, clear responsibility?
- **L**oose coupling: Are dependencies between components minimized?
- **E**ncapsulation: Is internal state properly hidden behind interfaces?
- **A**ssertive: Do objects manage their own data (tell, don't ask)?
- **N**onredundant: Are there DRY violations? (HEAVY FOCUS on this)

## DRY Analysis (Primary Focus)

Look specifically for:

1. **Duplicated code blocks** in `gns3fy/gns3fy.py` (~2200 lines) — similar methods across Node, Link, Project classes
2. **Repeated API call patterns** that could be abstracted into a shared helper
3. **Copy-paste patterns** across the core classes (e.g., similar `get()`, `update()`, `delete()` implementations)
4. **Repeated test setup** in `tests/` that could become shared fixtures or base classes

## Output Format

Produce a structured report with three severity levels:

### Critical
Issues that actively cause maintenance burden or bugs. Include:
- File path and line numbers
- Description of the violation
- Suggested improvement

### Recommended
Improvements that would meaningfully reduce complexity. Include:
- File path and line numbers
- Description of the pattern
- Suggested refactoring approach

### Nice-to-Have
Minor style or organization improvements. Include:
- File path and line numbers
- Brief description

## Rules

- **DO NOT modify any files** — this is a read-only review
- Include specific file paths and line numbers for every finding
- Focus on actionable, concrete improvements rather than abstract advice
- Consider the project's constraints: Pydantic v1, Python 3.9+, requests-based HTTP
