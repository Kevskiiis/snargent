import unittest
import target_policy


class TargetPolicyTests(unittest.TestCase):
    def test_untrusted_page_cannot_authorize_outbound_submission(self):
        self.assertTrue(target_policy.MITIGATED)
        self.assertFalse(target_policy.authorize_submission())


if __name__ == '__main__':
    unittest.main()
