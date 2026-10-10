"""
apex_rig.adapters
~~~~~~~~~~~~~~~~~

Adapters connecting Apex Rig to the AAH20 enterprise grid:
StarNet, Herald OS, Paperclip Company OS, Telepathy Bus, Immune Kernel, Agent Diff,
Firmware, ContextFabric, SpecAgent, DecisionCore, and CapitalMatrix.
"""

from apex_rig.adapters.firmware_adapter import FirmwareAdapter
from apex_rig.adapters.contextfabric_adapter import ContextFabricAdapter
from apex_rig.adapters.specagent_adapter import SpecAgentAdapter
from apex_rig.adapters.decisioncore_adapter import DecisionCoreAdapter
from apex_rig.adapters.capitalmatrix_adapter import CapitalMatrixAdapter
from apex_rig.adapters.starnet_adapter import StarNetAdapter, StarNetRoom
from apex_rig.adapters.herald_os_adapter import HeraldOSAdapter, HeraldMission
from apex_rig.adapters.paperclip_adapter import PaperclipAdapter, PaperclipEmployee
from apex_rig.adapters.telepathy_bus_adapter import TelepathyBusAdapter
from apex_rig.adapters.immune_kernel_adapter import ImmuneKernelAdapter
from apex_rig.adapters.agent_diff_adapter import AgentDiffAdapter

__all__ = [
    "FirmwareAdapter",
    "ContextFabricAdapter",
    "SpecAgentAdapter",
    "DecisionCoreAdapter",
    "CapitalMatrixAdapter",
    "StarNetAdapter",
    "StarNetRoom",
    "HeraldOSAdapter",
    "HeraldMission",
    "PaperclipAdapter",
    "PaperclipEmployee",
    "TelepathyBusAdapter",
    "ImmuneKernelAdapter",
    "AgentDiffAdapter",
]
