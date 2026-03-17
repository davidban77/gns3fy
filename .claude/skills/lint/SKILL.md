---
name: lint
description: Run ruff linting and formatting checks, auto-fix issues
user-invocable: true
argument-hint: "[--check-only]"
---

# Lint Skill

Run the project's linting and formatting pipeline, optionally auto-fixing issues.

## Instructions

1. Run `task lint` to check the current state of linting and formatting (includes security rules via ruff `S` rules).
2. If `$ARGUMENTS` contains `--check-only`, report the results and **stop** — do not fix anything.
3. Otherwise, run `task lint-fix` to auto-fix all fixable issues.
4. Re-run `task lint` to confirm everything is clean.
5. Run `task security` for deeper secret/credential scanning.
6. Report a summary of:
   - What was fixed (if anything)
   - Any remaining issues that require manual attention
   - Security scan findings (if any)
