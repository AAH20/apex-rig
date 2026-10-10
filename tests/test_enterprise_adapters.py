"""
Unit tests for enterprise grid adapters:
StarNet, Herald OS, Paperclip Company OS, Telepathy Bus, Immune Kernel, Agent Diff.
"""

import unittest
from apex_rig.adapters.starnet_adapter import StarNetAdapter
from apex_rig.adapters.herald_os_adapter import HeraldOSAdapter
from apex_rig.adapters.paperclip_adapter import PaperclipAdapter, PaperclipEmployee
from apex_rig.adapters.telepathy_bus_adapter import TelepathyBusAdapter
from apex_rig.adapters.immune_kernel_adapter import ImmuneKernelAdapter
from apex_rig.adapters.agent_diff_adapter import AgentDiffAdapter


class TestEnterpriseAdapters(unittest.TestCase):

    def test_starnet_adapter(self):
        starnet = StarNetAdapter(station_name="TestStation-01")
        room_eng = starnet.route_to_room("coding")
        self.assertIsNotNone(room_eng)
        self.assertEqual(room_eng.room_name, "Engineering Bay")

        telemetry = starnet.get_station_telemetry()
        self.assertEqual(telemetry["active_rooms"], 4)
        self.assertEqual(telemetry["station_name"], "TestStation-01")

    def test_herald_os_adapter(self):
        herald = HeraldOSAdapter(agent_name="Hermes-Test")
        mission = herald.submit_mission(
            workspace_name="work",
            title="Refactor Parser",
            instructions="Rewrite AST parser for streaming tokens",
        )
        self.assertEqual(mission.status, "active")
        self.assertEqual(mission.workspace_name, "work")

        ok = herald.complete_mission(mission.mission_id, success=True)
        self.assertTrue(ok)
        self.assertEqual(mission.status, "completed")

    def test_paperclip_adapter(self):
        paperclip = PaperclipAdapter(company_name="Apex Holdings")
        ledger = paperclip.get_company_ledger()
        self.assertGreaterEqual(ledger["headcount"], 3)
        self.assertGreater(ledger["total_budget_allocated_usd"], 0.0)

        # Budget check
        can_spend = paperclip.can_spend("emp-dev-01", 10.0)
        self.assertTrue(can_spend)
        cannot_spend = paperclip.can_spend("emp-dev-01", 999999.0)
        self.assertFalse(cannot_spend)

        # Record spend
        paperclip.record_payroll_spend("emp-dev-01", 5.25)
        self.assertEqual(paperclip._employees["emp-dev-01"].budget_spent_usd, 5.25)

        # Manager approval requirement
        self.assertFalse(paperclip.requires_manager_approval("emp-dev-01", blast_radius_files=2))
        self.assertTrue(paperclip.requires_manager_approval("emp-dev-01", blast_radius_files=5))

    def test_telepathy_bus_adapter(self):
        bus = TelepathyBusAdapter(ring_capacity=100)
        msg_id = bus.broadcast_telepathy(
            sender_harness="claude-01",
            topic="code_diff_ready",
            payload={"files": ["kernel.py"]},
        )
        self.assertTrue(len(msg_id) > 0)

        messages = bus.read_latest(topic="code_diff_ready", limit=5)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["sender"], "claude-01")

    def test_immune_kernel_adapter(self):
        immune = ImmuneKernelAdapter()
        # High clearance agent
        self.assertTrue(immune.check_capability("mock-fast-01", "write", "/system/config"))

        # Quarantine check
        immune.quarantine_agent("suspicious-agent", reason="Byzantine hallucination")
        self.assertTrue(immune.is_quarantined("suspicious-agent"))
        self.assertFalse(immune.check_capability("suspicious-agent", "read", "file.py"))

    def test_agent_diff_adapter(self):
        diff_adapter = AgentDiffAdapter()
        diff_safe = "--- file.py\n+++ file.py\n+ def new_helper():\n+     return True"
        report_safe = diff_adapter.analyze_diff("file.py", diff_safe)
        self.assertEqual(report_safe["verdict"], "APPROVED")
        self.assertFalse(report_safe["suspicious_guard_removal"])

        diff_unsafe = "--- file.py\n+++ file.py\n- assert user.is_authenticated()\n+ pass"
        report_unsafe = diff_adapter.analyze_diff("file.py", diff_unsafe)
        self.assertEqual(report_unsafe["verdict"], "FLAGGED")
        self.assertTrue(report_unsafe["suspicious_guard_removal"])


if __name__ == "__main__":
    unittest.main()
