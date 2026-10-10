"""
apex_rig.harness.process_supervisor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Harness supervisor managing pool of agents, priority task queue, and health lifecycle.
"""

from typing import Dict, List, Optional
import heapq
import time
from apex_rig.harness.base import BaseHarness
from apex_rig.core.primitives import (
    TaskSpec,
    TaskResult,
    HarnessDescriptor,
    HarnessState,
    HarnessType,
)


class ProcessSupervisor:
    """
    Central supervisor orchestrating a swarm of heterogeneous agent harnesses.
    """

    def __init__(self):
        self._harnesses: Dict[str, BaseHarness] = {}
        self._task_queue: List[tuple] = []  # Priority queue: (priority, timestamp, task)

    def register_harness(self, harness: BaseHarness) -> None:
        self._harnesses[harness.harness_id] = harness
        harness.start()

    def get_harness(self, harness_id: str) -> Optional[BaseHarness]:
        return self._harnesses.get(harness_id)

    def list_harnesses(self) -> List[HarnessDescriptor]:
        return [h.get_descriptor() for h in self._harnesses.values()]

    def enqueue_task(self, task: TaskSpec) -> None:
        """
        Enqueues task into the priority min-heap.
        """
        heapq.heappush(self._task_queue, (task.priority, task.created_at, task))

    def dispatch_next_task(self) -> Optional[TaskResult]:
        """
        Pulls highest priority task and dispatches to an idle or best-fit harness.
        """
        if not self._task_queue:
            return None

        _, _, task = heapq.heappop(self._task_queue)

        # Find idle harness matching capability or first available
        target_harness = None
        for h in self._harnesses.values():
            if h.state == HarnessState.IDLE:
                target_harness = h
                break

        if not target_harness:
            # Fallback to harness with least completed tasks
            target_harness = min(self._harnesses.values(), key=lambda h: h.tasks_completed)

        return target_harness.execute_task(task)

    def execute_immediate(self, task: TaskSpec, preferred_harness_id: Optional[str] = None) -> TaskResult:
        if preferred_harness_id and preferred_harness_id in self._harnesses:
            harness = self._harnesses[preferred_harness_id]
        else:
            # Pick first available or lowest load
            harness = min(self._harnesses.values(), key=lambda h: (h.state != HarnessState.IDLE, h.tasks_completed))
        return harness.execute_task(task)

    def stop_all(self) -> None:
        for h in self._harnesses.values():
            h.stop()

    def get_aggregate_stats(self) -> Dict[str, float]:
        total_tasks = sum(h.tasks_completed for h in self._harnesses.values())
        total_tokens = sum(h.total_tokens_consumed for h in self._harnesses.values())
        return {
            "registered_harnesses": float(len(self._harnesses)),
            "queued_tasks": float(len(self._task_queue)),
            "total_tasks_completed": float(total_tasks),
            "total_tokens_consumed": float(total_tokens),
        }
