"""
apex_rig.adapters.herald_os_adapter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adapter interfacing with Herald OS (agent-native desktop interface for Hermes Agent).
Bridges Herald mission planning, workspace routines, and voice/text directives to Apex Rig.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import time


@dataclass
class HeraldMission:
    mission_id: str
    workspace_name: str           # "work", "personal", "ideas"
    title: str
    instructions: str
    hermes_model: str = "hermes-3-llama-3.1-8b"
    status: str = "pending"       # "pending", "active", "completed", "aborted"
    created_at: float = field(default_factory=time.time)


class HeraldOSAdapter:
    """
    Coordinates Herald OS desktop workspaces and Hermes Agent routines with Apex Rig.
    """

    def __init__(self, agent_name: str = "Hermes-Prime"):
        self.agent_name = agent_name
        self._missions: Dict[str, HeraldMission] = {}
        self.active_workspace = "work"

    def submit_mission(
        self,
        workspace_name: str,
        title: str,
        instructions: str,
        hermes_model: str = "hermes-3-llama-3.1-8b",
    ) -> HeraldMission:
        """
        Dispatches a user mission from Herald OS dashboard into Apex Rig.
        """
        mid = f"mission_{int(time.time() * 1000)}_{len(self._missions)}"
        mission = HeraldMission(
            mission_id=mid,
            workspace_name=workspace_name,
            title=title,
            instructions=instructions,
            hermes_model=hermes_model,
            status="active",
        )
        self._missions[mid] = mission
        return mission

    def complete_mission(self, mission_id: str, success: bool = True) -> bool:
        if mission_id in self._missions:
            self._missions[mission_id].status = "completed" if success else "aborted"
            return True
        return False

    def get_herald_status(self) -> Dict[str, Any]:
        return {
            "herald_agent": self.agent_name,
            "active_workspace": self.active_workspace,
            "total_missions": len(self._missions),
            "pending_missions": sum(1 for m in self._missions.values() if m.status == "active"),
            "system_mode": "agent_native_desktop",
        }
