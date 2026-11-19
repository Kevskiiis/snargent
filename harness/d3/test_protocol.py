import unittest
from protocol import aggregate, schedule


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


if __name__ == '__main__':
    unittest.main()
