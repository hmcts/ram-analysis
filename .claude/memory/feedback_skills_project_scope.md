---
name: Skills go in project scope, not user scope
description: When creating skills for this user, place them in the project's .claude/skills/ directory by default — not ~/.claude/skills/
type: feedback
originSessionId: 9a236153-4b99-4505-911a-c9107f950ba1
---
When the user asks for a skill to be created, default to project scope (`<repo>/.claude/skills/<skill-name>/`) rather than user scope (`~/.claude/skills/`).

**Why:** the user wants skills tracked alongside the project (committable to the repo, scoped to the project's domain) rather than living globally on their machine. Confirmed when they explicitly redirected a skill from `~/.claude/skills/` to project scope.

**How to apply:** unless the user explicitly says "global skill" or "user-level skill", create skills under `<repo-root>/.claude/skills/<skill-name>/` with the standard layout (`SKILL.md`, plus optional `assets/`, `scripts/`, `templates/`, `references/`). If you've already placed something under `~/.claude/skills/` for them, move it.
