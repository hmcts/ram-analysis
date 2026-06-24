# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is **not** a runtime application — it is a Claude Code project that ships four reusable slash commands as its sole deliverable:

| Slash command | Output |
|---|---|
| `/docs-to-c4` | Structurizr DSL workspace + browsable static C4 site |
| `/create-data-dependency-architecture` | Styled PDF cataloguing inbound + outbound data dependencies |
| `/create-functional-modules-architecture` | Styled PDF cataloguing functional modules |
| `/check-for-owasp-top10` | Markdown + PDF audit against OWASP Top 10 for Agentic Applications 2026 |

`README.md` is the authoritative user-facing reference for each command — prerequisites, usage, output shape, and the per-command pipeline sequence diagrams all live there. Read it before changing any skill's pipeline; the document shape and re-run guarantees described there are part of the contract.

There is no build, no test suite, no lint step at the repo level. The "code" is the skills themselves: shell scripts, Python helpers, Markdown specs and Markdown templates under `.claude/lib/`.

## Architecture

Every slash command follows the same three-layer shape:

1. **Entry point** — `.claude/commands/<name>.md`: thin frontmatter + a pointer to the SKILL.md spec. Never put logic here.
2. **Pipeline spec** — `.claude/lib/<name>/SKILL.md`: numbered phases the model executes end-to-end. Co-located with the skill's `scripts/`, `templates/`, `references/` and (for `docs-to-c4`) `assets/`.
3. **Shared library** — `.claude/lib/_shared/`: the house PDF pipeline (CSS, Mermaid config, `build-pdf.sh`, `md_to_pdf.py`, `distil-binary-data.sh`) consumed by three of the four commands. Leading underscore is the "not a skill, supporting library" convention.

Consumer map:

- `create-data-dependency-architecture`, `create-functional-modules-architecture` — use `_shared/distil-binary-data.sh` (Phase 1) **and** `_shared/build-pdf.sh` (final phase)
- `check-for-owasp-top10` — uses `_shared/build-pdf.sh` only (works against source code, not binaries)
- `docs-to-c4` — independent toolchain (Java + `structurizr-site-generatr`); does not touch `_shared/`

### Hard rules when editing skills

- **No per-skill copies of shared assets.** `doc-style.css` and `mermaid-config.json` live in `_shared/assets/` and nowhere else. Edit there to change the look of every PDF; don't fork. The single sanctioned divergence is the OWASP report's Risk Status Board palette, which lives as a Mermaid `classDef` inside the report markdown.
- **Call into `_shared/` by absolute repo-rooted path**, e.g. `.claude/lib/_shared/scripts/build-pdf.sh <md>` — not by relative path. `md_to_pdf.py` resolves its asset paths relative to its own location, so the scripts cannot be moved out of `_shared/scripts/python/` without an update there.
- **All output goes inside `<input_folder>/output/`** (or `<input_folder>/output-functional-modules/`, or `<input_folder>/security/owasp/` for the OWASP skill). The repo running the command is never written to; tooling lives with the skill, data lives with the input folder.
- **Source documents under `<input_folder>` are read-only.** Distillation writes to `output/extracted-text/`; nothing modifies the originals.
- **Re-run semantics matter.** `docs-to-c4` is idempotent (overwrites). The three PDF skills are deterministic (byte-equivalent modulo PNG rasterisation). Preserve those guarantees when editing pipelines.

## Common commands

**Verify `/docs-to-c4` prerequisites** (Java 25, Python 3, structurizr-site-generatr, bmad-distillator):

```sh
bash .claude/lib/docs-to-c4/scripts/check_prereqs.sh
```

**Build a PDF from a markdown file** without going through a slash command (useful when iterating on `doc-style.css` or templates):

```sh
.claude/lib/_shared/scripts/build-pdf.sh path/to/file.md
```

On first run this script bootstraps a virtual environment at `.claude/lib/_shared/scripts/python/.venv/` and installs `weasyprint` from `requirements.txt`. Delete the venv to force a rebuild. The wrapper prepends the venv's `bin/` to `PATH` so pandoc finds `weasyprint`.

**Distil binary documents to plain text** (for inspecting what the pipelines see):

```sh
.claude/lib/_shared/scripts/distil-binary-data.sh /path/to/folder
```

Outputs land in `/path/to/folder/output/extracted-text/`.

## Repository-specific constraints

- **Git/GitHub writes are blocked from inside Claude sessions.** A `PreToolUse` Bash hook at `.claude/hooks/block-git-writes.sh` denies `git commit/push/pull/merge/rebase/reset/checkout/branch/tag/stash/cherry-pick/clean/rm` and any `gh`/`hub` invocation. Read-only git (`status`, `log`, `diff`, `show`, `blame`, `ls-files`, `config`, `remote`, `fetch`) is allowed. The user commits externally via VSCode after reviewing the diff. Do not try to work around the hook — surface the diff and stop.
- **`_bmad/` and `.claude/skills/bmad-*` are gitignored.** They are user-local plugin installs (the BMAD-METHOD plugin) and aren't part of the deliverable. `bmad-distillator` is a runtime dependency of `/docs-to-c4` — install the plugin to get it, don't add it to the repo.
- **The `_bmad-output/` folder is local scratch** (brainstorming, planning artefacts). It is not part of any pipeline's output contract.
- **`scripts/`, `sql/`, `docs/`, `resources/`, `openspec/` at the repo root are legacy/exploratory content** from earlier iterations — they are not consumed by any of the four slash commands. Don't wire new skill code through them. New skill files belong under `.claude/lib/<skill>/`.
- **`.github/CONTRIBUTING.md` is stale template boilerplate** (references Spring Boot / HMCTS) inherited from the repo template. Ignore its content; this repo's actual scope is the four slash commands described in `README.md`.
