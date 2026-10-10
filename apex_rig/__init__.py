"""
apex_rig
~~~~~~~~

Apex Rig: Sovereign Multi-Harness Aggregator, Hardware-Aware Router & Agent Mesh.
"""

from apex_rig.orchestrator import ApexRigOrchestrator
from apex_rig.core.primitives import (
    TaskSpec,
    TaskResult,
    RoutingDecision,
    ModelTier,
    HarnessType,
    HarnessState,
)
from apex_rig.core.radix_trie import PrefixRadixTrie
from apex_rig.core.entropy_router import EntropyRouter
from apex_rig.core.vram_projector import VRAMProjector
from apex_rig.core.workspace_journal import WorkspaceJournal
from apex_rig.core.evolution_engine import RigEvolutionEngine

__version__ = "1.0.0"
__all__ = [
    "ApexRigOrchestrator",
    "TaskSpec",
    "TaskResult",
    "RoutingDecision",
    "ModelTier",
    "HarnessType",
    "HarnessState",
    "PrefixRadixTrie",
    "EntropyRouter",
    "VRAMProjector",
    "WorkspaceJournal",
    "RigEvolutionEngine",
]
