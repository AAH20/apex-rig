"""
Unit tests for HardwareProber and LLMFitEngine.
"""

import unittest
from apex_rig.silicon.hardware_prober import HardwareProber
from apex_rig.silicon.llmfit_engine import LLMFitEngine


class TestSiliconEngine(unittest.TestCase):

    def test_hardware_prober(self):
        prober = HardwareProber()
        info = prober.probe()
        self.assertIn("os", info)
        self.assertIn("total_ram_mb", info)
        self.assertGreater(info["total_ram_mb"], 1024.0)

    def test_llmfit_small_model_fits(self):
        engine = LLMFitEngine(host_vram_mb=24576.0, host_ram_mb=65536.0)
        res = engine.evaluate_fit("qwen-2.5-coder-7b", param_count_b=7.0, quantization="Q4_K_M", context_tokens=8192)

        self.assertTrue(res.fits_in_vram)
        self.assertTrue(res.fits_in_ram)
        self.assertGreater(res.projected_tok_s, 10.0)

    def test_llmfit_giant_model_vram_overflow(self):
        # 8GB VRAM card trying to load 70B model
        small_engine = LLMFitEngine(host_vram_mb=8192.0, host_ram_mb=32768.0)
        res = small_engine.evaluate_fit("llama-3.3-70b", param_count_b=70.0, quantization="FP16", context_tokens=8192)

        self.assertFalse(res.fits_in_vram)


if __name__ == "__main__":
    unittest.main()
