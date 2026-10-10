"""
apex_rig.silicon
~~~~~~~~~~~~~~~~

Host silicon profiling, LLMFit dynamic estimation, and local runners.
"""

from apex_rig.silicon.hardware_prober import HardwareProber
from apex_rig.silicon.llmfit_engine import LLMFitEngine, FitResult
from apex_rig.silicon.local_runner import LocalRunner

__all__ = [
    "HardwareProber",
    "LLMFitEngine",
    "FitResult",
    "LocalRunner",
]
