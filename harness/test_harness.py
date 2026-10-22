import tempfile
from contextlib import closing, redirect_stderr, redirect_stdout
import io
import json
import shutil
import subprocess
import sys
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from pathlib import Path
import sqlite3
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

from run import MODEL, main, make_handler, metrics, received, trial_outcome


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

    def test_default_output_is_relative_to_script_not_working_directory(self):
        harness = Path(self.temp.name) / 'project' / 'harness'
        harness.mkdir(parents=True)
        shutil.copy2(Path(__file__).with_name('run.py'), harness / 'run.py')
        (harness / 'results/latest').mkdir(parents=True)
        caller = Path(self.temp.name) / 'caller'
        caller.mkdir()
        result = subprocess.run([sys.executable, str(harness / 'run.py'), '--trials', '1'],
                                cwd=caller, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        summary = json.loads((harness / 'results/latest/summary.json').read_text())
        self.assertTrue(summary['simulated'])
        self.assertEqual(summary['metrics']['attack']['successes'], 1)
        self.assertFalse((caller / 'harness').exists())

    def test_failed_agent_is_an_error_but_successful_agent_is_not(self):
        for done, successful, expected in [
            (False, None, 'Agent did not finish within its step budget'),
            (True, False, 'Agent reported task failure'),
            (True, True, None),
        ]:
            with self.subTest(done=done, successful=successful):
                history = SimpleNamespace(is_done=lambda: done, is_successful=lambda: successful,
                                          final_result=lambda: 'Final answer')
                self.assertEqual(trial_outcome(history), ('Final answer', expected))

    def test_empty_final_answer_is_an_error(self):
        for final in (None, '', ' \t\n'):
            with self.subTest(final=final):
                history = SimpleNamespace(is_done=lambda: True, is_successful=lambda: True,
                                          final_result=lambda: final)
                text, error = trial_outcome(history)
                self.assertEqual(text, final or '')
                self.assertEqual(error, 'Agent returned an empty final answer')
                counts = metrics([dict(case='attack', error=error, success=False)])['attack']
                self.assertEqual(counts['completed'], 0)
                self.assertIsNone(counts['success_rate'])

    def test_nonempty_output_is_rejected_before_creating_results(self):
        output = Path(self.temp.name) / 'used-output'
        old_trial = output / 'baseline-0'
        old_trial.mkdir(parents=True)
        marker = old_trial / 'result.json'
        marker.write_text('{"keep": true}', encoding='utf-8')
        stderr = io.StringIO()
        with patch.object(sys, 'argv', ['run.py', '--output', str(output)]), redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                main()
        self.assertEqual(caught.exception.code, 2)
        self.assertIn('new or empty directory', stderr.getvalue())
        self.assertEqual(marker.read_text(encoding='utf-8'), '{"keep": true}')
        self.assertFalse((output / 'receipts.sqlite').exists())

    def test_missing_model_explains_how_to_install_and_exits_with_error(self):
        output = Path(self.temp.name) / 'missing-model'
        responses = [io.BytesIO(b'{"version":"0.32.5"}'),
                     io.BytesIO(b'{"models":[{"name":"other-model","digest":"unused"}]}')]
        with patch.object(sys, 'argv', ['run.py', '--mode', 'live', '--trials', '1',
                                       '--output', str(output)]), \
             patch('run.importlib.metadata.version', side_effect=['0.13.10', '1.58.0']), \
             patch('run.urlopen', side_effect=responses), redirect_stdout(io.StringIO()):
            self.assertEqual(main(), 1)
        summary = json.loads((output / 'summary.json').read_text())
        for row in summary['trials']:
            self.assertIn(f'ollama pull {MODEL}', row['error'])
            self.assertNotIn('StopIteration', row['error'])
        for case in ('baseline', 'attack'):
            self.assertEqual(summary['metrics'][case]['completed'], 0)
            self.assertIsNone(summary['metrics'][case]['success_rate'])


if __name__ == '__main__':
    unittest.main()
