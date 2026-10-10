"""
apex_rig.harness.mock_harness
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deterministic high-speed mock harness for unit testing, benchmarking, and simulation.
"""

import time
from typing import Optional
from apex_rig.harness.base import BaseHarness
from apex_rig.core.primitives import (
    TaskSpec,
    TaskResult,
    HarnessType,
    HarnessState,
)


class MockHarness(BaseHarness):
    """
    Simulated harness with deterministic token metrics and synthetic latency.
    """

    def __init__(
        self,
        harness_id: str = "mock-harness-01",
        harness_type: HarnessType = HarnessType.MOCK,
        synthetic_latency_ms: float = 5.0,
    ):
        super().__init__(harness_id, harness_type)
        self.synthetic_latency_ms = synthetic_latency_ms

    def start(self) -> bool:
        self.state = HarnessState.IDLE
        return True

    def stop(self) -> bool:
        self.state = HarnessState.TERMINATED
        return True

    def execute_task(self, task: TaskSpec) -> TaskResult:
        self.state = HarnessState.RUNNING
        self.current_task = task
        t_start = time.perf_counter()

        # Simulate fast execution
        if self.synthetic_latency_ms > 0:
            time.sleep(self.synthetic_latency_ms / 1000.0)

        in_tokens = max(10, len(task.prompt) // 4)
        out_tokens = max(15, in_tokens // 2)
        self.total_tokens_consumed += (in_tokens + out_tokens)
        self.tasks_completed += 1

        t_elapsed_ms = (time.perf_counter() - t_start) * 1000.0
        self.state = HarnessState.IDLE
        self.current_task = None

        return TaskResult(
            task_id=task.task_id,
            status="completed",
            output_text=f"[Mock Response] Executed prompt: {task.prompt[:64]}...",
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            cost_usd=round((in_tokens * 0.25 + out_tokens * 1.0) / 1e6, 6),
            latency_ms=round(t_elapsed_ms, 2),
            provider="mock_engine",
            model_id="mock-v1",
            harness_id=self.harness_id,
            speculative_accepted=True,
            metadata={"priority": task.priority},
        )
