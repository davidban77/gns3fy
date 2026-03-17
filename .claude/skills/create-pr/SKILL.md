---
name: create-pr
description: Create a descriptive GitHub PR with summary and test plan using gh CLI
user-invocable: true
argument-hint: "[base branch, defaults to develop]"
---

# Create PR Skill

Create a well-structured GitHub Pull Request using the `gh` CLI.

## Instructions

1. Determine the base branch:
   - Use `$ARGUMENTS` if provided, otherwise default to `develop`.
2. Gather context by running:
   - `git log <base>..HEAD --oneline` — all commits in this branch
   - `git diff <base>...HEAD --stat` — changed files summary
   - `git branch --show-current` — current branch name
3. Push the branch if needed: `git push -u origin HEAD`
4. **Analyze ALL commits** (not just the latest) to understand the full scope of changes.
5. Create the PR using `gh pr create`:
   - **Title**: Under 70 characters, descriptive of the overall change
   - **Body** using this template:

   ```markdown
   ## Summary
   - <1-3 bullet points describing what changed and why>

   ## Changes
   - <key file modifications and their purpose>

   ## Test plan
   - [ ] <specific testing steps relevant to the changes>
   ```

6. Use a HEREDOC to pass the body to ensure correct formatting:
   ```bash
   gh pr create --title "..." --body "$(cat <<'EOF'
   ## Summary
   ...
   EOF
   )"
   ```
7. Return the PR URL when done.
