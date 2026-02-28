#!/usr/bin/env python3
"""CortexLog: AI-agent-first work memory CLI backed by append-only JSONL."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List


DEFAULT_DB_PATH = Path('.cortexlog.jsonl')


@dataclass(frozen=True)
class Entry:
    ts: str
    kind: str
    note: str
    tags: List[str]
    goal: str
    decision: str
    next_actions: List[str]
    task: str
    files: List[str]

    @property
    def day(self) -> str:
        return self.ts[:10]


def parse_tags(raw: str) -> List[str]:
    if not raw:
        return []
    parts = [p.strip().lower() for p in raw.split(',') if p.strip()]
    return list(dict.fromkeys(parts))


def normalize_text_items(raw: str) -> List[str]:
    if not raw:
        return []
    parts = [p.strip() for p in raw.split(',') if p.strip()]
    return list(dict.fromkeys(parts))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def to_entry(item: dict) -> Entry:
    # Backward compatibility for legacy rows with only ts/note/tags.
    return Entry(
        ts=item['ts'],
        kind=item.get('kind', 'note'),
        note=item.get('note', ''),
        tags=item.get('tags', []),
        goal=item.get('goal', ''),
        decision=item.get('decision', ''),
        next_actions=item.get('next_actions', []),
        task=item.get('task', ''),
        files=item.get('files', []),
    )


def read_entries(path: Path) -> List[Entry]:
    if not path.exists():
        return []

    entries: List[Entry] = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        entries.append(to_entry(json.loads(line)))
    return entries


def append_entry(path: Path, payload: dict) -> Entry:
    row = {
        'ts': payload.get('ts', now_iso()),
        'kind': payload.get('kind', 'note'),
        'note': payload.get('note', '').strip(),
        'tags': payload.get('tags', []),
        'goal': payload.get('goal', '').strip(),
        'decision': payload.get('decision', '').strip(),
        'next_actions': payload.get('next_actions', []),
        'task': payload.get('task', '').strip(),
        'files': payload.get('files', []),
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=True))
        f.write('\n')
    return to_entry(row)


def token_blob(e: Entry) -> str:
    parts = [
        e.kind,
        e.note,
        e.goal,
        e.decision,
        e.task,
        ' '.join(e.tags),
        ' '.join(e.next_actions),
        ' '.join(e.files),
    ]
    return ' '.join(parts).lower()


def compute_open_tasks(entries: Iterable[Entry]) -> List[str]:
    open_tasks: dict[str, str] = {}
    for e in entries:
        if e.kind == 'checkpoint':
            for task in e.next_actions:
                key = task.strip().lower()
                if key:
                    open_tasks[key] = task
        elif e.kind == 'resolve' and e.task.strip():
            open_tasks.pop(e.task.strip().lower(), None)
    return list(open_tasks.values())


def cmd_add(args: argparse.Namespace) -> int:
    tags = parse_tags(args.tags)
    entry = append_entry(Path(args.db), {'kind': 'note', 'note': args.note, 'tags': tags})
    print(f"Added note [{entry.ts}] {entry.note}")
    if entry.tags:
        print(f"Tags: {', '.join(entry.tags)}")
    return 0


def cmd_checkpoint(args: argparse.Namespace) -> int:
    tags = parse_tags(args.tags)
    files = normalize_text_items(args.files)
    next_actions: List[str] = []
    for block in args.next:
        next_actions.extend(normalize_text_items(block))

    entry = append_entry(
        Path(args.db),
        {
            'kind': 'checkpoint',
            'goal': args.goal,
            'decision': args.decision,
            'next_actions': next_actions,
            'tags': tags,
            'files': files,
            'note': args.note,
        },
    )

    print(f"Checkpoint [{entry.ts}] recorded")
    print(f"Goal: {entry.goal}")
    print(f"Decision: {entry.decision}")
    if entry.next_actions:
        print('Next actions:')
        for task in entry.next_actions:
            print(f"  - {task}")
    if entry.files:
        print(f"Files: {', '.join(entry.files)}")
    return 0


def cmd_resolve(args: argparse.Namespace) -> int:
    entry = append_entry(
        Path(args.db),
        {'kind': 'resolve', 'task': args.task, 'note': args.note, 'tags': parse_tags(args.tags)},
    )
    print(f"Resolved [{entry.ts}] {entry.task}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    entries = read_entries(Path(args.db))
    if args.day:
        entries = [e for e in entries if e.day == args.day]
    if args.kind:
        entries = [e for e in entries if e.kind == args.kind]

    if not entries:
        print('No entries found.')
        return 0

    for idx, e in enumerate(entries, start=1):
        headline = e.note or e.goal or e.task or e.decision or '(empty)'
        print(f"{idx}. {e.ts} [{e.kind}] {headline}")
        if e.tags:
            print(f"   tags: {', '.join(e.tags)}")
        if e.next_actions:
            print(f"   next: {', '.join(e.next_actions)}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    query = args.query.lower()
    entries = read_entries(Path(args.db))
    if args.kind:
        entries = [e for e in entries if e.kind == args.kind]

    hits = [e for e in entries if query in token_blob(e)]
    if not hits:
        print('No matches found.')
        return 0

    for idx, e in enumerate(hits, start=1):
        headline = e.note or e.goal or e.task or e.decision or '(empty)'
        print(f"{idx}. {e.ts} [{e.kind}] {headline}")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    entries = read_entries(Path(args.db))
    if not entries:
        print('No entries found.')
        return 0

    by_day = Counter(e.day for e in entries)
    by_tag = Counter(tag for e in entries for tag in e.tags)
    by_kind = Counter(e.kind for e in entries)

    print('Entries by day:')
    for day, count in sorted(by_day.items()):
        print(f"  {day}: {count}")

    print('Entries by kind:')
    for kind, count in sorted(by_kind.items()):
        print(f"  {kind}: {count}")

    print('Tag usage:')
    if not by_tag:
        print('  (no tags)')
    else:
        for tag, count in by_tag.most_common():
            print(f"  {tag}: {count}")
    return 0


def cmd_handoff(args: argparse.Namespace) -> int:
    entries = read_entries(Path(args.db))
    if not entries:
        print('No entries found.')
        return 0

    subset = entries[-args.limit :]
    checkpoints = [e for e in subset if e.kind == 'checkpoint']
    latest_checkpoint = checkpoints[-1] if checkpoints else None
    open_tasks = compute_open_tasks(entries)

    if args.format == 'json':
        payload = {
            'generated_at': now_iso(),
            'entries_considered': len(subset),
            'latest_goal': latest_checkpoint.goal if latest_checkpoint else '',
            'latest_decision': latest_checkpoint.decision if latest_checkpoint else '',
            'open_tasks': open_tasks,
            'recent_entries': [
                {
                    'ts': e.ts,
                    'kind': e.kind,
                    'note': e.note,
                    'goal': e.goal,
                    'decision': e.decision,
                    'task': e.task,
                    'next_actions': e.next_actions,
                }
                for e in subset
            ],
        }
        print(json.dumps(payload, ensure_ascii=True, indent=2))
        return 0

    print('AGENT HANDOFF')
    print(f"Generated: {now_iso()}")
    print(f"Entries considered: {len(subset)}")
    if latest_checkpoint:
        print(f"Current goal: {latest_checkpoint.goal}")
        print(f"Latest decision: {latest_checkpoint.decision}")
    else:
        print('Current goal: (none)')
        print('Latest decision: (none)')

    print('Open tasks:')
    if not open_tasks:
        print('  - (none)')
    else:
        for task in open_tasks:
            print(f"  - {task}")

    print('Recent timeline:')
    for e in subset:
        headline = e.note or e.goal or e.task or e.decision or '(empty)'
        print(f"  - {e.ts} [{e.kind}] {headline}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='CortexLog: AI-agent memory CLI (append-only JSONL)')
    parser.add_argument('--db', default=str(DEFAULT_DB_PATH), help='Path to JSONL storage file')

    sub = parser.add_subparsers(dest='command', required=True)

    add_p = sub.add_parser('add', help='Add a free-form note')
    add_p.add_argument('note', help='Entry text to store')
    add_p.add_argument('--tags', default='', help='Comma-separated tags')
    add_p.set_defaults(func=cmd_add)

    cp_p = sub.add_parser('checkpoint', help='Capture agent goal/decision/next-actions state')
    cp_p.add_argument('--goal', required=True, help='Current objective')
    cp_p.add_argument('--decision', required=True, help='Most important decision taken')
    cp_p.add_argument(
        '--next',
        required=True,
        action='append',
        help='Next action(s), repeatable or comma-separated',
    )
    cp_p.add_argument('--files', default='', help='Comma-separated touched files')
    cp_p.add_argument('--tags', default='', help='Comma-separated tags')
    cp_p.add_argument('--note', default='', help='Optional context note')
    cp_p.set_defaults(func=cmd_checkpoint)

    resolve_p = sub.add_parser('resolve', help='Mark an open task as done')
    resolve_p.add_argument('task', help='Task text matching an earlier next-action')
    resolve_p.add_argument('--note', default='', help='Optional resolution note')
    resolve_p.add_argument('--tags', default='', help='Comma-separated tags')
    resolve_p.set_defaults(func=cmd_resolve)

    list_p = sub.add_parser('list', help='List entries')
    list_p.add_argument('--day', default='', help='Filter by day (YYYY-MM-DD)')
    list_p.add_argument('--kind', default='', help='Filter by kind: note|checkpoint|resolve')
    list_p.set_defaults(func=cmd_list)

    search_p = sub.add_parser('search', help='Search notes/checkpoints/tasks/tags/files')
    search_p.add_argument('query', help='Case-insensitive search query')
    search_p.add_argument('--kind', default='', help='Filter by kind: note|checkpoint|resolve')
    search_p.set_defaults(func=cmd_search)

    stats_p = sub.add_parser('stats', help='Show summary statistics')
    stats_p.set_defaults(func=cmd_stats)

    handoff_p = sub.add_parser('handoff', help='Generate context handoff for another agent')
    handoff_p.add_argument('--limit', type=int, default=20, help='Number of recent entries to include')
    handoff_p.add_argument('--format', choices=['prompt', 'json'], default='prompt', help='Output format')
    handoff_p.set_defaults(func=cmd_handoff)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    raise SystemExit(main())
