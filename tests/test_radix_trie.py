"""
Unit tests for PrefixRadixTrie context deduplication.
"""

import unittest
from apex_rig.core.radix_trie import PrefixRadixTrie


class TestPrefixRadixTrie(unittest.TestCase):

    def setUp(self):
        self.trie = PrefixRadixTrie(avg_chars_per_token=4.0)

    def test_single_registration(self):
        prefix = "System: You are an autonomous software engineering agent.\nHere is the codebase map:\n- src/main.py\n- src/utils.py\n"
        pid, shared, unique = self.trie.register_prefix(prefix, "agent_1")
        self.assertTrue(len(pid) > 0)
        self.assertEqual(shared, 0)
        self.assertGreater(unique, 0)

    def test_duplicate_registration_savings(self):
        prefix = "System: Common prompt prelude across all coding agents in the swarm.\n"
        _, shared_1, unique_1 = self.trie.register_prefix(prefix, "agent_1")
        _, shared_2, unique_2 = self.trie.register_prefix(prefix, "agent_2")
        _, shared_3, unique_3 = self.trie.register_prefix(prefix, "agent_3")

        self.assertEqual(shared_1, 0)
        self.assertGreater(shared_2, 0)
        self.assertGreater(shared_3, 0)

        metrics = self.trie.get_metrics()
        self.assertGreater(metrics["savings_percentage"], 50.0)
        self.assertGreater(metrics["tokens_saved"], 0)

    def test_empty_prefix(self):
        pid, shared, unique = self.trie.register_prefix("", "agent_empty")
        self.assertEqual(pid, "")
        self.assertEqual(shared, 0)
        self.assertEqual(unique, 0)


if __name__ == "__main__":
    unittest.main()
