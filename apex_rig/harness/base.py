"""
apex_rig.harness.base
~~~~~~~~~~~~~~~~~~~~~

Abstract BaseHarness interface for all agent execution harnesses.
"""

from abc import ABC, abstractmethod
from typing import Optional
from apex_rig.core.primitives import (
    TaskSpec,
    TaskResult,
    HarnessDescriptor,
    HarnessType,
    HarnessState,
)


class BaseHarness(ABC):
    """
    Standard interface wrapping any agent CLI, subprocess, or in-memory agent.
    """

    def __init__(self, harness_id: str, harness_type: HarnessType):
        self.harness_id = harness_id
        self.harness_type = harness_type
        self.state = HarnessState.IDLE
        self.current_task: Optional[TaskSpec] = None
        self.tasks_completed = 0
        self.total_tokens_consumed = 0

    @abstractmethod
    def start(self) -> bool:
        """Initializes the execution sandbox/environment."""
        pass

    @abstractmethod
    def stop(self) -> bool:
        """Gracefully shuts down the harness."""
        pass

    @abstractmethod
    def execute_task(self, task: TaskSpec) -> TaskResult:
        """Executes a single task within the harness context."""
        pass

    def get_descriptor(self) -> HarnessDescriptor:
        return HarnessDescriptor(
            harness_id=self.harness_id,
            harness_type=self.harness_type,
            state=self.state,
            current_task_id=self.current_task.task_id if self.current_task else None,
            active_context_tokens=self.total_tokens_consumed,
            resident_memory_mb=128.0,
            tasks_completed=self.tasks_completed,
            uptime_sec=100.0,
        )
