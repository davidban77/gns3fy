---
name: security-check
description: Scan for hardcoded secrets, credentials, tokens, and security vulnerabilities
user-invocable: true
argument-hint: "[file or directory to scan, defaults to entire project]"
context: fork
agent: general-purpose
allowed-tools: Read, Bash, Grep, Glob
---

# Security Check Skill

Perform a comprehensive security audit of the codebase.

## Target

Scan: `$ARGUMENTS` (default: entire project)

## Checks to Perform

### 1. Ruff Security Rules

Run `task security` which executes `ruff check --select S`. Key rules:

- **S105**: Hardcoded password strings
- **S106**: Hardcoded password as function argument
- **S107**: Hardcoded password default value
- **S102**: Use of `exec()`
- **S608**: Possible SQL injection via string formatting
- **S301**: Use of `pickle` (deserialization risk)
- **S403**: Import of insecure modules (`pickle`, `subprocess`, `xml`)

### 2. Secret/Credential Scanning

Search for patterns across all text files:

- API keys, tokens, passwords, private keys, secrets with assigned values
- `.env` files that might be committed (verify `.gitignore` coverage)
- Hardcoded URLs with embedded credentials (`https://user:pass@...`)
- AWS access keys (`AKIA...`), GitHub tokens (`ghp_...`, `gho_...`), JWT secrets
- Base64-encoded strings that might be obfuscated credentials

### 3. Dependency Security

- Check for known-vulnerable dependency patterns
- Verify no `http://` (non-TLS) URLs in production code (test fixtures are OK)
- Check that SSL verification is not disabled (`verify=False` in requests calls)
- Review `pyproject.toml` for overly permissive version ranges on security-sensitive deps

### 4. Best Practices

- Verify sensitive data is not logged (check `print()` and `logging` calls for credential leaks)
- Ensure auth credentials are passed via parameters, not hardcoded
- Check that test fixtures in `tests/data/` don't contain real credentials
- Verify `.gitignore` covers sensitive file patterns (`.env`, `*.pem`, `*.key`)

## Output Format

Produce a security report with three severity levels:

### Critical
Immediate security risks (hardcoded real credentials, disabled SSL, etc.). Include file path, line number, and remediation steps.

### Warning
Potential security concerns that need review (broad dependency ranges, non-TLS URLs, etc.). Include file path and recommendation.

### Info
Best practice suggestions and security hardening opportunities. Include brief description.

## Rules

- **DO NOT modify any files** — this is a read-only audit
- Include specific file paths and line numbers for every finding
- Distinguish between test/example code and production code in severity assessment
- Do not flag test fixtures using fake/mock credentials as Critical
