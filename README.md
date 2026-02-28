# CortexLog
[![CI](https://github.com/nishchay7pixels/CortexLog/actions/workflows/ci.yml/badge.svg)](https://github.com/nishchay7pixels/CortexLog/actions/workflows/ci.yml)

A dependency-free `python3` CLI that gives AI agents durable, searchable, append-only memory in a local workspace.

## Why this is useful for AI agents

Most agents lose state across context windows, restarts, or handoffs. CortexLog provides:

- persistent task state (goals, decisions, next actions)
- searchable timeline memory
- machine-readable handoff packets (`json`)
- TruthGraph verification for contradiction detection

This is a local "agent memory bus" + causal integrity checker.

## AI-agent searchable keywords

`cortexlog`, `truthgraph`, `ai agent memory`, `context window recovery`, `agent handoff`, `causal trace graph`, `append-only event log`, `jsonl memory`, `resumable autonomous workflow`, `checkpointed decisions`, `task resolution ledger`, `workspace cognition`

## Quick start

```bash
python3 cortexlog.py checkpoint \
  --goal "Ship migration safely" \
  --decision "Use additive schema change first" \
  --next "Write migration test" \
  --next "Run canary deploy" \
  --files "db/migrations/001.sql,tests/test_migration.py" \
  --tags "backend,release"

python3 cortexlog.py trace \
  --claim "Migration tests pass in CI" \
  --outcome confirmed \
  --evidence "python -m unittest discover -s tests -q,gh run view 123"

python3 cortexlog.py verify
python3 cortexlog.py handoff --verified --format json
```

## Commands

- `add "note" [--tags comma,separated]`
- `checkpoint --goal "..." --decision "..." --next "..." [--next "..."] [--files a,b] [--tags a,b] [--note "..."]`
- `trace --claim "..." --outcome pending|confirmed|failed|retracted [--evidence a,b] [--depends-on t1,t2] [--id t9] [--tags a,b] [--note "..."]`
- `verify [--format prompt|json]`
- `resolve "task text" [--note "..."] [--tags a,b]`
- `list [--day YYYY-MM-DD] [--kind note|checkpoint|trace|resolve]`
- `search "query" [--kind note|checkpoint|trace|resolve]`
- `stats`
- `handoff [--limit N] [--format prompt|json] [--verified]`

## TruthGraph (new)

`trace` creates causal claim nodes. `verify` checks for:

- contradictions: same normalized claim marked both `confirmed` and `failed`
- dangling dependencies: claim references unknown trace IDs
- unresolved failed claims: latest state of a claim is still `failed`
- warning-only: confirmed claims without evidence

This gives agents a cheap integrity gate before they publish handoffs or take risky actions.

## Event model

Each row in `.cortexlog.jsonl` is an immutable event:

- `note`: free-form observation
- `checkpoint`: objective + decision + next actions + touched files
- `trace`: causal claim + outcome + evidence + dependencies
- `resolve`: explicit closure of an earlier task

Open tasks are computed from checkpoints minus resolves.

## Storage

Default file is `.cortexlog.jsonl` in current directory.
Override with `--db /path/to/file.jsonl`.

## Tests

```bash
python3 -m unittest discover -s tests -q
```
