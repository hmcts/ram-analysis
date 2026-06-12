---
name: Git default branch should be main
description: When initializing new git repos, use main as the initial branch name, not master
type: feedback
originSessionId: 78ccc64c-2a6b-404a-86fc-3ed062f2031c
---
When running `git init` or creating new repositories, the initial branch must be `main`, not `master`.

**Why:** User explicitly corrected this after a `git init` defaulted to `master`. Modern convention and user preference.

**How to apply:** Either run `git init -b main` from the start, or set it globally via `git config --global init.defaultBranch main`. If a repo was already initialized with `master`, rename with `git branch -m main`.
