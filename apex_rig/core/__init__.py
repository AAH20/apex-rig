"""
apex_rig.core
~~~~~~~~~~~~~

Public exports for Apex Rig core engines and primitives.
"""

from apex_rig.core.primitives import (
    HarnessType,
    HarnessState,
    ModelTier,
    ModelDescriptor,
    TaskSpec,
    TaskResult,
    HarnessDescriptor,
    RoutingDecision,
    HardwareTelemetry,
    JournalEntry,
    EvolutionGenome,
)
from apex_rig.core.radix_trie import PrefixRadixTrie, RadixNode
from apex_rig.core.entropy_router import EntropyRouter
from apex_rig.core.vram_projector import VRAMProjector
from apex_rig.core.workspace_journal import WorkspaceJournal
from apex_rig.core.evolution_engine import RigEvolutionEngine

__all__ = [
    "HarnessType",
    "HarnessState",
    "ModelTier",
    "ModelDescriptor",
    "TaskSpec",
    "TaskResult",
    "HarnessDescriptor",
    "RoutingDecision",
    "HardwareTelemetry",
    "JournalEntry",
    "EvolutionGenome",
    "PrefixRadixTrie",
    "RadixNode",
    "EntropyRouter",
    "VRAMProjector",
    "WorkspaceJournal",
    "RigEvolutionEngine",
]
