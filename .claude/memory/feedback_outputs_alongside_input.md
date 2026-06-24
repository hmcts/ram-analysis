---
name: Outputs go alongside input data, not in the running project
description: Skill outputs (rendered docs, intermediate artefacts, distilled text) must be written under `<input-folder>/output/`, never inside the repo running the tooling. Tooling and data stay separated.
type: feedback
originSessionId: cd9c8504-8d02-4ffd-a881-84629cac5d70
---
When a skill produces output from a user-supplied input folder, every per-run artefact — distilled text, intermediate build markdown, rendered Markdown, PDF, diagram PNGs — must be written under `<input-folder>/output/`, alongside the input data. The repo running the tooling is **never** written to during a run.

**Why:** the user explicitly asked for "the tooling can be differentiated from the data that it produces or consumes". Mixing per-run artefacts into the running project (e.g. `docs/architecture/`, `.tmp/extracted-text/`) makes the skill not self-contained: the project accumulates state from every run, and the same skill invoked against a different docs folder leaks artefacts back into whichever repo Claude happened to be in. Outputs alongside input is also the convention already used by the sibling `docs-to-c4` skill.

**How to apply:**

- The user's `docs/` directory in any project is **not** an output destination for these skills — don't write there, and don't put authoring guides, style references or build scripts there either. (The original "docs/ holds outputs only" rule is superseded.)
- For `create-data-dependency-architecture`: outputs go to `<input-folder>/output/{extracted-text/, data-dependencies.md, data-dependencies.pdf, data-dependencies.assets/}`.
- For `docs-to-c4`: outputs go to `<input-folder>/output/{converted/, distilled/, workspace.dsl, site/, README.md}`.
- The script `distil-binary-data.sh` defaults its output dir to `<input-folder>/output/extracted-text/` if the second argument is omitted.
- Skill internals (`SKILL.md`, `assets/`, `scripts/`, `templates/`, `references/`) stay with the skill at `.claude/lib/<skill>/` — that's where the tooling lives, separate from any data.
- The script's `find -maxdepth 1 -type f` keeps the new `output/` subfolder from being re-ingested on subsequent runs.
