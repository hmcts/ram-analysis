---
name: No GitHub operations from Claude sessions
description: Never perform any GitHub operations (commits, pushes, PRs, branch ops, gh CLI calls) from within Claude sessions
type: feedback
originSessionId: 50073e4d-7a37-4257-bbe1-f30d3559e32f
---
DO NOT perform any GitHub operations from within Claude sessions. This includes `git commit`, `git push`, `gh pr create`, branch operations, and any other interaction with GitHub or remote git state.

**Why:** The user handles all git/GitHub commits externally via VSCode after personally reviewing the work. Claude making commits or pushing bypasses that review step.

**How to apply:** Make local code edits freely, but stop short of any git state-changing command. Read-only git inspection (`git status`, `git diff`, `git log`) is fine for understanding context. If a task seems to require a commit/push/PR, surface the change for the user to commit themselves rather than executing it.
