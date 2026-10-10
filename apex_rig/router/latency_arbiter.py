"""
apex_rig.router.latency_arbiter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dynamic latency and TTFT outlier monitor for multi-provider arbitration.
Identifies degraded upstream services and reroutes requests before timeouts occur.
"""

from typing import Dict, List, Optional
from collections import deque
import math
import time


class LatencyArbiter:
    """
    Rolling statistical tracker of provider response times.
    """

    def __init__(self, window_size: int = 30, outlier_sigma: float = 2.0):
        self.window_size = window_size
        self.outlier_sigma = outlier_sigma
        self._samples: Dict[str, deque] = {}

    def record_latency(self, provider: str, latency_ms: float) -> None:
        if provider not in self._samples:
            self._samples[provider] = deque(maxlen=self.window_size)
        self._samples[provider].append(latency_ms)

    def is_degraded(self, provider: str, current_latency_ms: float) -> bool:
        samples = self._samples.get(provider)
        if not samples or len(samples) < 5:
            return False

        mean = sum(samples) / len(samples)
        variance = sum((x - mean) ** 2 for x in samples) / len(samples)
        std_dev = max(10.0, math.sqrt(variance))

        threshold = mean + (self.outlier_sigma * std_dev)
        return current_latency_ms > threshold

    def get_provider_stats(self, provider: str) -> Dict[str, float]:
        samples = self._samples.get(provider)
        if not samples:
            return {"samples": 0.0, "mean_ms": 0.0, "std_dev_ms": 0.0}

        mean = sum(samples) / len(samples)
        variance = sum((x - mean) ** 2 for x in samples) / len(samples)
        std_dev = math.sqrt(variance)
        return {
            "samples": float(len(samples)),
            "mean_ms": round(mean, 2),
            "std_dev_ms": round(std_dev, 2),
            "p95_ms": round(sorted(samples)[int(0.95 * len(samples))], 2),
        }
