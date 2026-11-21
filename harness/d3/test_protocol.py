import unittest
from pathlib import Path
import tempfile
from protocol import aggregate, schedule
from verify import resolve_evidence_path


class ProtocolTests(unittest.TestCase):
    def test_schedule_is_matched_deterministic_and_unique(self):
        rows = schedule()
        self.assertEqual(rows, schedule())
        self.assertEqual(len(rows), 120)
        self.assertEqual(len({r['canary'] for r in rows}), 120)
        self.assertEqual(len({r['trial_id'] for r in rows}), 120)
        for row in rows:
            self.assertRegex(row['trial_id'], r'^[-a-zA-Z0-9_]{1,128}$')

    def test_partial_and_duplicate_evidence_rejected(self):
        rows = schedule()
        with self.assertRaisesRegex(ValueError, 'Missing'):
            aggregate(rows, [])
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            aggregate(rows, [rows[0], rows[0]])

    def test_errors_remain_in_denominator_and_smoke_is_rejected(self):
        plans = schedule()
        rows = [dict(p, mitigated=False, mode='live', model_digest='test-only',
                     status='timeout', collector_exact_match=False, task_completed=False,
                     payload_observed=None, trace_path='test-only', receipt_path='test-only')
                for p in plans]
        totals = aggregate(plans, rows)
        self.assertEqual(sum(r['total'] for r in totals), 120)
        self.assertEqual(sum(r['timeout'] for r in totals), 120)
        rows[0]['mode'] = 'smoke'
        with self.assertRaisesRegex(ValueError, 'live'):
            aggregate(plans, rows)

    def test_evidence_paths_accept_windows_and_posix_separators(self):
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root) / 'harness' / 'd3' / 'evidence' / 'run'
            path = directory / 'trial' / 'messages.jsonl'
            path.parent.mkdir(parents=True)
            path.write_text('')
            stored_windows = str(path.relative_to(directory.parents[4])).replace('/', '\\')
            stored_posix = path.relative_to(directory.parents[4]).as_posix()

            original_root = __import__('verify').ROOT
            __import__('verify').ROOT = directory.parents[4]
            try:
                self.assertEqual(resolve_evidence_path(stored_windows, directory), path.resolve())
                self.assertEqual(resolve_evidence_path(stored_posix, directory), path.resolve())
            finally:
                __import__('verify').ROOT = original_root

    def test_evidence_paths_cannot_escape_the_run_directory(self):
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root) / 'evidence' / 'run'
            directory.mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, 'unsafe'):
                resolve_evidence_path('../outside.json', directory)


if __name__ == '__main__':
    unittest.main()
