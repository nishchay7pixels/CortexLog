import json
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from tools.cortexlog import append_entry, compute_open_tasks, main, parse_tags, read_entries


class CortexLogTests(unittest.TestCase):
    def test_parse_tags_dedupes_and_normalizes(self):
        self.assertEqual(parse_tags('Bug, bug,  Focus ,'), ['bug', 'focus'])

    def test_backward_compatible_read_of_legacy_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / '.cortexlog.jsonl'
            db.write_text(
                '{"ts":"2026-02-28T12:00:00+00:00","note":"legacy","tags":["x"]}\n',
                encoding='utf-8',
            )
            entries = read_entries(db)
            self.assertEqual(entries[0].kind, 'note')
            self.assertEqual(entries[0].note, 'legacy')

    def test_open_tasks_from_checkpoint_and_resolve(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / '.cortexlog.jsonl'
            append_entry(
                db,
                {
                    'ts': '2026-02-28T12:00:00+00:00',
                    'kind': 'checkpoint',
                    'goal': 'Ship feature',
                    'decision': 'Use jsonl',
                    'next_actions': ['Write tests', 'Update docs'],
                },
            )
            append_entry(
                db,
                {
                    'ts': '2026-02-28T12:10:00+00:00',
                    'kind': 'resolve',
                    'task': 'Write tests',
                },
            )

            open_tasks = compute_open_tasks(read_entries(db))
            self.assertEqual(open_tasks, ['Update docs'])

    def test_handoff_json_contains_open_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / '.cortexlog.jsonl'
            append_entry(
                db,
                {
                    'ts': '2026-02-28T12:00:00+00:00',
                    'kind': 'checkpoint',
                    'goal': 'Goal A',
                    'decision': 'Decision A',
                    'next_actions': ['Task A'],
                },
            )

            with patch('sys.stdout', new_callable=StringIO) as out:
                rc = main(['--db', str(db), 'handoff', '--format', 'json'])
            self.assertEqual(rc, 0)
            payload = json.loads(out.getvalue())
            self.assertEqual(payload['latest_goal'], 'Goal A')
            self.assertEqual(payload['open_tasks'], ['Task A'])


if __name__ == '__main__':
    unittest.main()
