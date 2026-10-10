"""
apex_rig.silicon.llmfit_engine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dynamic model-to-silicon fit calculator, quantization selector, and OOM predictor.
Transcends static llmfit by calculating memory requirements across expanding context lengths.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from apex_rig.core.vram_projector import VRAMProjector


@dataclass
class FitResult:
    model_name: str
    param_count_b: float
    quantization: str
    target_context_tokens: int
    weight_memory_mb: float
    kv_cache_memory_mb: float
    total_memory_mb: float
    fits_in_vram: bool
    fits_in_ram: bool
    projected_tok_s: float
    safety_margin_pct: float


class LLMFitEngine:
    """
    Evaluates model memory footprints and projects throughput for on-device deployment.
    """

    QUANT_BITS = {
        "Q4_0": 4.5,
        "Q4_K_M": 4.8,
        "Q8_0": 8.5,
        "FP8": 8.0,
        "FP16": 16.0,
    }

    def __init__(self, host_vram_mb: float = 24576.0, host_ram_mb: float = 65536.0, memory_bandwidth_gb_s: float = 200.0):
        self.host_vram_mb = host_vram_mb
        self.host_ram_mb = host_ram_mb
        self.memory_bandwidth_gb_s = memory_bandwidth_gb_s

    def evaluate_fit(
        self,
        model_name: str,
        param_count_b: float,
        quantization: str = "Q4_K_M",
        context_tokens: int = 8192,
    ) -> FitResult:
        bits_per_param = self.QUANT_BITS.get(quantization, 4.8)
        # Weight memory in MB: (params_billion * 1e9 * bits / 8) / 1024^2
        weight_bytes = (param_count_b * 1e9 * bits_per_param) / 8.0
        weight_mb = weight_bytes / (1024.0 * 1024.0)

        # Dynamic KV-cache memory in MB
        kv_mb = VRAMProjector.estimate_kv_cache_size_mb(context_tokens=context_tokens)

        # Total memory with 10% activation buffer
        total_mb = (weight_mb + kv_mb) * 1.10

        fits_vram = total_mb <= (self.host_vram_mb * 0.90)
        fits_ram = total_mb <= (self.host_ram_mb * 0.85)

        # Theoretical memory-bandwidth bound generation speed
        model_size_gb = total_mb / 1024.0
        projected_tok_s = (self.memory_bandwidth_gb_s / max(0.5, model_size_gb)) * 0.65  # 65% efficiency

        headroom = max(0.0, (self.host_vram_mb - total_mb) / self.host_vram_mb) * 100.0

        return FitResult(
            model_name=model_name,
            param_count_b=param_count_b,
            quantization=quantization,
            target_context_tokens=context_tokens,
            weight_memory_mb=round(weight_mb, 1),
            kv_cache_memory_mb=round(kv_mb, 1),
            total_memory_mb=round(total_mb, 1),
            fits_in_vram=fits_vram,
            fits_in_ram=fits_ram,
            projected_tok_s=round(projected_tok_s, 1),
            safety_margin_pct=round(headroom, 1),
        )

    def scan_catalog(self, context_tokens: int = 8192) -> List[FitResult]:
        catalog = [
            ("qwen-2.5-coder-3b", 3.0),
            ("qwen-2.5-coder-7b", 7.0),
            ("llama-3.1-8b", 8.0),
            ("deepseek-coder-14b", 14.0),
            ("qwen-2.5-32b", 32.0),
            ("llama-3.3-70b", 70.0),
        ]
        results = []
        for name, params in catalog:
            res = self.evaluate_fit(name, params, "Q4_K_M", context_tokens)
            results.append(res)
        return results
