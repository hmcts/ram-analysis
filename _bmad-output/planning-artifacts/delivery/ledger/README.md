# Ledger (sharded per epic)

The traceability ledger is **sharded — one file per epic** (`epic-0.0.yaml` … `epic-0.5.yaml`) — so multiple people can update different epics concurrently without git conflicts. Because the dispatch graph pushes work to run in parallel across different epics/repos, concurrent writers naturally touch **different shards**. Rationale and the full concurrency model: [`../README.md`](../README.md).

## Shard schema

```yaml
epic: epic-0.1                 # epic id (matches dispatch-graph.yaml)
title: ...
repo: ram-reference-data       # owning repo, or a list when the epic spans repos
bus_version: arch-v1.0
status: not-started            # EPIC-LEVEL rollup (see vocab below)
owner: null                    # who is driving this epic (name/handle); null = unassigned
stories:
  - story: 0.1.1
    repo: ram-reference-data   # per-story repo (may differ from the epic within a multi-repo epic)
    title: ...
    frs: [FR6, FR7, FR8]       # traced requirements (epic granularity unless a story narrows it)
    bus_version: arch-v1.0     # the ram-architecture version the story was built against
    status: not-started        # STORY-LEVEL lifecycle (see vocab below)
    owner: null                # who is on this story; null = unassigned
    pr: null                   # PR URL once opened/merged
```

## Status vocab

- **Epic-level** (`status:` at the top): `not-started` · `in-progress` · `blocked` · `in-review` · `done`.
- **Story-level** (`status:` on each story): `not-started` → `dispatched` → `in-progress` → `in-review` → `done`.
  - `dispatched` = story packet generated into the target repo (**this is the claim** — set `owner` and push promptly to prevent double-pickup).

## Ownership & visibility ("who is working on what")

- **Epic `owner`** = the person accountable for the epic end-to-end.
- **Story `owner`** = the person currently implementing that story (lets two people share one epic on different stories).
- To see the whole board at a glance, scan the six shards' epic headers (`status` + `owner`); for finer detail, the per-story `owner`/`status`.

## Concurrency rules

- **Pull `main` before** you select / dispatch / signal.
- **Claim before you start:** set story `status: dispatched` + `owner`, and push, before writing code — that is the lock.
- **One story = one small, atomic commit/PR** to the shard.
- **Work in parallel by epic/repo, not within a repo** — keeps writers off each other's shards.
- Roll the epic-level `status`/`owner` up from its stories (e.g. epic → `in-progress` when its first story is `dispatched`; `done` when all stories are `done`).

## Target state (projection)

Once the service repos exist, the authoritative story status will live in each repo (story-packet frontmatter + PR state), and a resolver will **regenerate** these shards as a read-only rollup — no hand-editing, no contention — the same producer-owned / read-only-mirror principle used for API contracts. Until then, these shards are hand-maintained.
