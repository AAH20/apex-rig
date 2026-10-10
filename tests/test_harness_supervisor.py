"""
Unit tests for ProcessSupervisor and agent harnesses.
"""

import unittest
from apex_rig.harness.process_supervisor import ProcessSupervisor
from apex_rig.harness.mock_harness import MockHarness
from apex_rig.harness.claude_code_harness import ClaudeCodeHarness
from apex_rig.harness.aider_harness import AiderHarness
from apex_rig.core.primitives import TaskSpec, HarnessState


class TestHarnessSupervisor(unittest.TestCase):

    def setUp(self):
        self.supervisor = ProcessSupervisor()
        self.mock_h = MockHarness("mock-01", synthetic_latency_ms=1.0)
        self.claude_h = ClaudeCodeHarness("claude-01")
        self.aider_h = AiderHarness("aider-01")

        self.supervisor.register_harness(self.mock_h)
        self.supervisor.register_harness(self.claude_h)
        self.supervisor.register_harness(self.aider_h)

    def test_harness_registration(self):
        descriptors = self.supervisor.list_harnesses()
        self.assertEqual(len(descriptors), 3)

    def test_immediate_task_execution(self):
        task = TaskSpec(task_id="t1", prompt="Optimize Python sorting loop")
        res = self.supervisor.execute_immediate(task, preferred_harness_id="mock-01")
        self.assertEqual(res.status, "completed")
        self.assertEqual(res.harness_id, "mock-01")
        self.assertGreater(res.output_tokens, 0)

    def test_priority_queue_dispatch(self):
        t_low = TaskSpec(task_id="t_low", prompt="Low priority clean", priority=200)
        t_high = TaskSpec(task_id="t_high", prompt="Critical crash fix", priority=5)

        self.supervisor.enqueue_task(t_low)
        self.supervisor.enqueue_task(t_high)

        # High priority should be dispatched first
        res_first = self.supervisor.dispatch_next_task()
        self.assertIsNotNone(res_first)
        self.assertEqual(res_first.task_id, "t_high")

        res_second = self.supervisor.dispatch_next_task()
        self.assertIsNotNone(res_second)
        self.assertEqual(res_second.task_id, "t_low")


if __name__ == "__main__":
    unittest.main()
