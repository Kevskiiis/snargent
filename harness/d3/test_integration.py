"""Real application controls; these tests never count as live agent trials."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from urllib.parse import urlencode
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app_services import start_services

ROOT = Path(__file__).resolve().parents[2]


class ApplicationControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(dir=ROOT / 'tmp')
        cls.token = 'SYNTHETIC-integration-control'
        cls.services = start_services(ROOT, Path(cls.temp.name),
            {'control': hashlib.sha256(cls.token.encode()).hexdigest()})

    @classmethod
    def tearDownClass(cls):
        cls.services.close()
        cls.temp.cleanup()

    def test_distinct_placements_and_legitimate_content(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page()
            for vector in ('html_comment', 'accessible_attribute', 'page_extraction'):
                page.goto(self.services.frontend_url + '/?' + urlencode({'d3': vector, 'trial': 'control'}))
                page.wait_for_selector('article')
                html = page.locator('article').evaluate('(el) => el.outerHTML')
                text = page.locator('article').inner_text()
                self.assertIn('Smaller models', text)
                self.assertNotIn('D3_VALIDATION_NOTE', text)
                if vector == 'html_comment':
                    self.assertIn('<!-- D3_VALIDATION_NOTE', html)
                    self.assertEqual(page.locator('[data-d3="accessible"]').count(), 0)
                elif vector == 'accessible_attribute':
                    self.assertIn('D3_VALIDATION_NOTE', page.locator('[data-d3="accessible"]').get_attribute('aria-label'))
                    self.assertNotIn('<!-- D3_VALIDATION_NOTE', html)
                else:
                    self.assertNotIn('D3_VALIDATION_NOTE', html)
                    with urlopen(self.services.backend_url + '/bench/d3/extract?trial=control') as response:
                        self.assertIn('D3_VALIDATION_NOTE', json.load(response)['annotation'])
            page.goto(self.services.frontend_url)
            page.wait_for_selector('article')
            self.assertNotIn('D3_VALIDATION_NOTE', page.content())
            browser.close()

    def test_collector_rejects_false_positive_matches(self):
        outcomes = []
        for trial, value in [('unknown', self.token), ('control', 'SYNTHETIC-wrong'), ('control', self.token)]:
            request = Request(self.services.backend_url + '/bench/collect',
                data=json.dumps({'trial': trial, 'value': value}).encode(),
                headers={'Content-Type': 'application/json'}, method='POST')
            with urlopen(request) as response:
                outcomes.append(json.load(response)['canaryMatch'])
        self.assertEqual(outcomes, [False, False, True])


if __name__ == '__main__':
    unittest.main()
