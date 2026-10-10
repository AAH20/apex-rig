"""
Unit tests for WorkspaceJournal transactional staging and rollback.
"""

import unittest
from apex_rig.core.workspace_journal import WorkspaceJournal


class TestWorkspaceJournal(unittest.TestCase):

    def setUp(self):
        self.journal = WorkspaceJournal()

    def test_stage_and_commit(self):
        ok, msg, entry = self.journal.stage_change(
            harness_id="agent_a",
            file_path="src/kernel.py",
            action="modify",
            original_content="x = 1",
            new_content="x = 2",
        )
        self.assertTrue(ok)
        self.assertIsNotNone(entry)
        self.assertEqual(self.journal.get_pending_count("agent_a"), 1)

        committed = self.journal.commit_transaction("agent_a")
        self.assertEqual(len(committed), 1)
        self.assertTrue(committed[0].committed)
        self.assertEqual(self.journal.get_pending_count("agent_a"), 0)

    def test_stage_and_rollback(self):
        ok, _, _ = self.journal.stage_change(
            harness_id="agent_b",
            file_path="src/broken.py",
            action="create",
            original_content="",
            new_content="raise Exception()",
        )
        self.assertTrue(ok)
        rolled_back = self.journal.rollback_transaction("agent_b")
        self.assertEqual(len(rolled_back), 1)
        self.assertEqual(self.journal.get_pending_count("agent_b"), 0)

    def test_file_lock_collision(self):
        self.journal.stage_change(
            harness_id="agent_1",
            file_path="src/shared.py",
            action="modify",
            original_content="a = 1",
            new_content="a = 2",
        )
        # Agent 2 attempts to edit same file while locked by agent 1
        ok, msg, _ = self.journal.stage_change(
            harness_id="agent_2",
            file_path="src/shared.py",
            action="modify",
            original_content="a = 1",
            new_content="a = 3",
        )
        self.assertFalse(ok)
        self.assertIn("Conflict", msg)


if __name__ == "__main__":
    unittest.main()
