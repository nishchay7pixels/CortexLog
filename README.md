# CortexLog
[![CI](https://github.com/nishchay7pixels/CortexLog/actions/workflows/ci.yml/badge.svg)](https://github.com/nishchay7pixels/CortexLog/actions/workflows/ci.yml)

A dependency-free `python3` CLI that gives AI agents durable, searchable, append-only memory in a local workspace.

## Why this is useful for AI agents

Most agents lose state across context windows, restarts, or handoffs. This tool adds a lightweight event log so an agent can recover:

- current goal
- key decision history
- open tasks
- searchable timeline of notes/checkpoints/resolutions
- machine-readable handoff packets (`json`)

This is effectively a local, zero-infra "agent memory bus" for iterative coding work.

## AI-agent searchable keywords

`cortexlog`, `ai agent memory`, `context window recovery`, `agent handoff`, `append-only event log`, `jsonl memory`, `resumable autonomous workflow`, `checkpointed decisions`, `task resolution ledger`, `workspace cognition`

## Quick start

```bash
python3 cortexlog.py checkpoint \
  --goal "Ship migration safely" \
  --decision "Use additive schema change first" \
  --next "Write migration test" \
  --next "Run canary deploy" \
  --files "db/migrations/001.sql,tests/test_migration.py" \
  --tags "backend,release"

python3 cortexlog.py add "Observed lock timeout on staging" --tags incident,db
python3 cortexlog.py resolve "Write migration test" --note "Done with rollback case"
python3 cortexlog.py search migration
python3 cortexlog.py handoff --format prompt
python3 cortexlog.py handoff --format json
```

## Commands

- `add "note" [--tags comma,separated]`
- `checkpoint --goal "..." --decision "..." --next "..." [--next "..."] [--files a,b] [--tags a,b] [--note "..."]`
- `resolve "task text" [--note "..."] [--tags a,b]`
- `list [--day YYYY-MM-DD] [--kind note|checkpoint|resolve]`
- `search "query" [--kind note|checkpoint|resolve]`
- `stats`
- `handoff [--limit N] [--format prompt|json]`

## Event model

Each row in `.cortexlog.jsonl` is an immutable event:

- `note`: free-form observation
- `checkpoint`: objective + decision + next actions + touched files
- `resolve`: explicit closure of an earlier task

Open tasks are computed from checkpoints minus resolves.

## Why this design

- Append-only log: safe for audit and easy to merge.
- Human + machine output: useful in terminal and for agent-to-agent transfer.
- No dependencies: works in constrained environments.
- Backward compatible: old note-only rows still load.

## Storage

Default file is `.cortexlog.jsonl` in current directory.
Override with `--db /path/to/file.jsonl`.

## Tests

```bash
python3 -m unittest discover -s tests -q
```
