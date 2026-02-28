# CortexLog FAQ

## What is CortexLog in one line?

A local append-only memory CLI for humans and AI agents to track goals, decisions, claims, and handoffs.

## Where is data stored?

By default in `.cortexlog.jsonl` in your current directory.

Use a custom path with:

```bash
python3 cortexlog.py --db /path/to/project-memory.jsonl ...
```

## Can I use one log per project?

Yes. Run CortexLog from each project root, or pass a unique `--db` path.

## What does `verify` failing mean?

`verify` fails when TruthGraph finds at least one blocking issue:

- contradiction (same claim both confirmed and failed)
- dangling dependency (`depends_on` references unknown trace id)
- unresolved failed claim (latest status is still failed)

It returns exit code `1` on failure.

## Why does `verify` mention "missing evidence" but still pass?

Confirmed claims without evidence are currently warnings, not blockers.

## How should I write good `trace` claims?

Good claims are specific and testable.

Examples:

- Good: `CSV endpoint returns valid RFC4180 header`
- Weak: `CSV is better now`

## I see duplicate tasks in open tasks. Why?

Task matching is based on normalized task text. Keep task wording consistent between `checkpoint --next` and `resolve`.

## Can humans use this without AI agents?

Yes. It works as a structured engineering journal with verification and handoff snapshots.

## How do I start clean for a new project phase?

Create a new DB file path, or archive old entries and keep a fresh file:

```bash
mv .cortexlog.jsonl .cortexlog.archive.jsonl
```

## How do I inspect raw events quickly?

```bash
tail -n 20 .cortexlog.jsonl
```

## How can I search only trace claims?

```bash
python3 cortexlog.py search "rate limiter" --kind trace
```
