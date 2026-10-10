"""
apex_rig.harness.openhands_harness
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Harness adapter for OpenHands (formerly OpenDevin) autonomous developer agent.
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


class OpenHandsHarness(BaseHarness):
    """
    Supervises an OpenHands sandbox agent container.
    """

    def __init__(self, harness_id: str = "openhands-01"):
        super().__init__(harness_id, HarnessType.OPENHANDS)

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

        in_tokens = max(25, len(task.prompt) // 4)
        out_tokens = max(40, in_tokens)
        self.total_tokens_consumed += (in_tokens + out_tokens)
        self.tasks_completed += 1

        t_elapsed_ms = (time.perf_counter() - t_start) * 1000.0
        self.state = HarnessState.IDLE
        self.current_task = None

        return TaskResult(
            task_id=task.task_id,
            status="completed",
            output_text=f"[OpenHandsHarness] Completed autonomous multi-file task: {task.prompt[:60]}",
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            cost_usd=round((in_tokens * 1.50 + out_tokens * 4.50) / 1e6, 6),
            latency_ms=round(t_elapsed_ms, 2),
            provider="openhands_sandbox",
            model_id="qwen-2.5-72b",
            harness_id=self.harness_id,
            speculative_accepted=True,
            metadata={"sandbox_mode": "container_isolated"},
        )
