"""
Unit tests for VRAMProjector and memory growth projection.
"""

import unittest
import time
from apex_rig.core.vram_projector import VRAMProjector


class TestVRAMProjector(unittest.TestCase):

    def setUp(self):
        self.projector = VRAMProjector(total_vram_mb=16384.0, eviction_watermark=0.85)

    def test_kv_cache_estimation(self):
        # 32 layers, 32 heads, head dim 128, FP16 = 2 bytes per param
        size_4k = self.projector.estimate_kv_cache_size_mb(context_tokens=4096)
        size_32k = self.projector.estimate_kv_cache_size_mb(context_tokens=32768)

        self.assertGreater(size_32k, size_4k)
        self.assertAlmostEqual(size_32k / size_4k, 8.0, delta=0.1)

    def test_sample_and_growth_rate(self):
        t0 = time.time()
        self.projector.record_sample(allocated_vram_mb=8000.0, active_kv_cache_mb=500.0, timestamp=t0)
        telemetry = self.projector.record_sample(allocated_vram_mb=9000.0, active_kv_cache_mb=1500.0, timestamp=t0 + 2.0)

        self.assertGreater(telemetry.memory_growth_rate_mb_s, 0.0)
        self.assertGreater(telemetry.projected_headroom_sec, 0.0)

    def test_eviction_trigger(self):
        threshold = 16384.0 * 0.85  # 13926.4 MB
        needs_evict_false, _ = self.projector.should_evict(12000.0)
        needs_evict_true, excess = self.projector.should_evict(14500.0)

        self.assertFalse(needs_evict_false)
        self.assertTrue(needs_evict_true)
        self.assertGreater(excess, 0.0)


if __name__ == "__main__":
    unittest.main()
