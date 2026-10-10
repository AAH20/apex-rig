"""
apex_rig.core.vram_projector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dynamic VRAM Horizon and KV-Cache Memory Growth Rate Projector.
Calculates real-time derivative dM/dt, estimates time-to-exhaustion headroom,
and issues early eviction signals before Out-Of-Memory (OOM) faults occur.
"""

from typing import List, Dict, Optional, Tuple
from collections import deque
import time
from apex_rig.core.primitives import HardwareTelemetry


class VRAMProjector:
    """
    Predictive memory horizon estimator using a fixed-capacity ring buffer.
    """

    def __init__(
        self,
        total_vram_mb: float = 24576.0,    # Default 24GB VRAM
        eviction_watermark: float = 0.85,  # Trigger eviction at 85% capacity
        ring_buffer_capacity: int = 60,
    ):
        self.total_vram_mb = total_vram_mb
        self.eviction_watermark = eviction_watermark
        self.capacity_threshold_mb = total_vram_mb * eviction_watermark
        self._samples: deque = deque(maxlen=ring_buffer_capacity)

    def record_sample(
        self,
        allocated_vram_mb: float,
        active_kv_cache_mb: float,
        timestamp: Optional[float] = None,
    ) -> HardwareTelemetry:
        """
        Records a telemetry sample and calculates instantaneous dM/dt.
        """
        now = timestamp if timestamp is not None else time.time()
        self._samples.append((now, allocated_vram_mb, active_kv_cache_mb))

        growth_rate_mb_s = self._calculate_growth_rate()
        free_vram_mb = max(0.0, self.total_vram_mb - allocated_vram_mb)

        # Calculate time headroom before crossing watermark
        headroom_mb = max(0.0, self.capacity_threshold_mb - allocated_vram_mb)
        if growth_rate_mb_s > 0.01:
            projected_headroom_sec = headroom_mb / growth_rate_mb_s
        else:
            projected_headroom_sec = 3600.0  # Safe (>1 hour)

        return HardwareTelemetry(
            host_os="darwin",
            total_ram_mb=65536.0,
            free_ram_mb=32768.0,
            total_vram_mb=self.total_vram_mb,
            free_vram_mb=round(free_vram_mb, 2),
            compute_device="mps/cuda",
            active_kv_cache_mb=round(active_kv_cache_mb, 2),
            memory_growth_rate_mb_s=round(growth_rate_mb_s, 3),
            projected_headroom_sec=round(projected_headroom_sec, 2),
            timestamp=now,
        )

    def _calculate_growth_rate(self) -> float:
        if len(self._samples) < 2:
            return 0.0

        # Linear regression / finite difference between oldest and newest in window
        t_first, m_first, _ = self._samples[0]
        t_last, m_last, _ = self._samples[-1]
        dt = t_last - t_first
        if dt <= 0.001:
            return 0.0

        return max(0.0, (m_last - m_first) / dt)

    def should_evict(self, current_allocated_mb: float) -> Tuple[bool, float]:
        """
        Returns (needs_eviction, excess_mb_to_evict)
        """
        if current_allocated_mb >= self.capacity_threshold_mb:
            excess = current_allocated_mb - (self.total_vram_mb * (self.eviction_watermark - 0.10))
            return (True, max(0.0, excess))
        return (False, 0.0)

    @staticmethod
    def estimate_kv_cache_size_mb(
        context_tokens: int,
        num_layers: int = 32,
        num_heads: int = 32,
        head_dim: int = 128,
        bytes_per_param: int = 2,  # FP16 = 2 bytes, FP8 = 1 byte
    ) -> float:
        """
        Calculates exact KV-cache size in megabytes:
        2 * n_layers * n_heads * head_dim * context_tokens * bytes_per_param / 1024^2
        """
        bytes_total = 2 * num_layers * num_heads * head_dim * context_tokens * bytes_per_param
        return round(bytes_total / (1024.0 * 1024.0), 3)
