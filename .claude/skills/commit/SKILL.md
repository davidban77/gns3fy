---
name: commit
description: Create a conventional commit from staged changes without Co-Authored-By
user-invocable: true
argument-hint: "[optional hint for commit scope/message]"
---

# Commit Skill

Create a well-formatted conventional commit from currently staged changes.

## Instructions

1. Run `git status` and `git diff --cached` to review staged changes.
2. If nothing is staged, inform the user and **stop**.
3. Run `git log --oneline -5` to check recent commit message style.
4. Generate a conventional commit message following this format:
   ```
   <type>(<scope>): <description>
   ```
   Where `<type>` is one of: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`, `build`, `perf`.
5. If `$ARGUMENTS` is provided, use it as a hint for the commit scope or message content.
6. **CRITICAL: NEVER add `Co-Authored-By` lines to the commit message.**
7. Create the commit using HEREDOC format:
   ```bash
   git commit -m "$(cat <<'EOF'
   <type>(<scope>): <description>

   <optional body with details>
   EOF
   )"
   ```
8. Show `git log --oneline -1` to confirm the commit was created successfully.
