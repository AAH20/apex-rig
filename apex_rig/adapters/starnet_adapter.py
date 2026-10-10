"""
apex_rig.adapters.starnet_adapter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adapter interfacing with StarNet (local-first desktop agent workspace).
Maps StarNet capability rooms to Apex Rig harnesses, memory bounds, and entropy routers.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import time


@dataclass
class StarNetRoom:
    room_id: str
    room_name: str
    assigned_harness_id: str
    capability: str
    active_tasks: int = 0
    local_only: bool = True


class StarNetAdapter:
    """
    Coordinates local desktop workspaces and capability rooms with StarNet.
    """

    def __init__(self, station_name: str = "StarStation-Alpha"):
        self.station_name = station_name
        self._rooms: Dict[str, StarNetRoom] = {}
        self._init_default_rooms()

    def _init_default_rooms(self) -> None:
        defaults = [
            StarNetRoom("room-eng", "Engineering Bay", "claude-01", "coding", local_only=False),
            StarNetRoom("room-arch", "Command Bridge", "mock-fast-01", "architecture", local_only=True),
            StarNetRoom("room-sec", "Security Air Lock", "aider-01", "security_audit", local_only=True),
            StarNetRoom("room-ops", "Telemetry Deck", "openhands-01", "operations", local_only=False),
        ]
        for r in defaults:
            self._rooms[r.room_id] = r

    def route_to_room(self, capability: str) -> Optional[StarNetRoom]:
        """Finds the designated capability room for a task."""
        for room in self._rooms.values():
            if room.capability == capability:
                return room
        return self._rooms.get("room-eng")

    def register_room(self, room: StarNetRoom) -> None:
        self._rooms[room.room_id] = room

    def get_station_telemetry(self) -> Dict[str, Any]:
        return {
            "station_name": self.station_name,
            "active_rooms": len(self._rooms),
            "rooms": [r.__dict__ for r in self._rooms.values()],
            "status": "orbiting_local_silicon",
        }
