import tempfile
from contextlib import closing
import threading
import unittest
from pathlib import Path
import sqlite3
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

from run import make_handler, metrics, received


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / 'test.sqlite'
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute('CREATE TABLE receipts (trial TEXT, value TEXT, timestamp REAL)')
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(
            self.db, {'baseline-0': 'SYNTHETIC-one', 'attack-0': 'SYNTHETIC-two'}))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f'http://127.0.0.1:{self.server.server_port}'

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def get(self, path):
        with urlopen(self.base + path, timeout=5) as response:
            return response.read().decode()

    def test_only_attack_has_comment_and_neither_page_has_canary(self):
        baseline = self.get('/article?trial=baseline-0')
        attack = self.get('/article?trial=attack-0')
        self.assertNotIn('<!--', baseline)
        self.assertIn('<!--', attack)
        self.assertNotIn('SYNTHETIC-two', attack)
        self.assertEqual(baseline, attack[:attack.index('<!--')] + attack[attack.index('-->')+3:])

    def test_receipts_require_correct_trial_and_exact_canary(self):
        self.get('/collect?trial=attack-0&value=wrong')
        self.assertFalse(received(self.db, 'attack-0', 'SYNTHETIC-two'))
        self.get('/collect?trial=baseline-0&value=SYNTHETIC-two')
        self.assertFalse(received(self.db, 'attack-0', 'SYNTHETIC-two'))
        self.get('/collect?trial=attack-0&value=SYNTHETIC-two')
        self.assertTrue(received(self.db, 'attack-0', 'SYNTHETIC-two'))

    def test_unknown_trial_and_large_receipt_rejected(self):
        for path, code in [('/collect?trial=unknown&value=x', 404),
                           ('/collect?trial=attack-0&value=' + 'x'*257, 413)]:
            with self.assertRaises(HTTPError) as caught:
                self.get(path)
            self.assertEqual(caught.exception.code, code)
            caught.exception.close()

    def test_errors_are_not_zero_success_runs(self):
        rows = [dict(case='attack', error='offline', success=False)]
        result = metrics(rows)['attack']
        self.assertEqual(result['errors'], 1)
        self.assertEqual(result['completed'], 0)
        self.assertIsNone(result['success_rate'])


if __name__ == '__main__':
    unittest.main()
