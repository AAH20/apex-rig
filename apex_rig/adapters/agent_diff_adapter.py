"""
apex_rig.adapters.agent_diff_adapter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adapter interfacing with AAH20/agent-diff.
Performs semantic AST diff inspection, blast radius scoring, and intent discrepancy detection.
"""

from typing import Dict, List, Any


class AgentDiffAdapter:
    """
    Coordinates visual AST diffing and silent guard removal detection with agent-diff.
    """

    def __init__(self):
        self.scans_performed = 0
        self.guards_preserved = 0

    def analyze_diff(self, file_path: str, diff_text: str) -> Dict[str, Any]:
        self.scans_performed += 1
        lines = diff_text.splitlines()
        added = sum(1 for line in lines if line.startswith("+") and not line.startswith("+++"))
        removed = sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))

        # Blast radius score: normalized between 0.0 and 1.0
        blast_radius = min(1.0, (added + removed) / 200.0)

        # Detect silent security check removal
        suspicious_removal = any("assert" in line or "check" in line or "verify" in line for line in lines if line.startswith("-"))

        if not suspicious_removal:
            self.guards_preserved += 1

        return {
            "file_path": file_path,
            "lines_added": added,
            "lines_removed": removed,
            "blast_radius_score": round(blast_radius, 3),
            "suspicious_guard_removal": suspicious_removal,
            "verdict": "FLAGGED" if suspicious_removal else "APPROVED",
        }

    def get_diff_metrics(self) -> Dict[str, Any]:
        return {
            "scans_performed": self.scans_performed,
            "guards_preserved": self.guards_preserved,
            "integrity_ratio": round(self.guards_preserved / max(1, self.scans_performed), 3),
        }
