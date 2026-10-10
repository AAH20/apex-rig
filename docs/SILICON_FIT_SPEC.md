# Apex Rig: Silicon Topology & Dynamic Memory Horizon Specification

---

## 1. Dynamic Autoregressive Memory Model

Static VRAM estimation fails during autoregressive generation because KV-cache size expands with context length $L$:

$$M_{\text{runtime}}(t) = M_{\text{weights}} + M_{\text{activations}} + M_{\text{kv\_cache}}(t)$$

### Exact KV-Cache Sizing Formulation
For transformer architectures with $N_L$ layers, $N_H$ key-value heads, head dimension $D_H$, precision bytes $B$ (FP16 = 2, FP8 = 1), and active sequence length $L$:

$$M_{\text{kv\_cache}}(\text{MB}) = \frac{2 \cdot N_L \cdot N_H \cdot D_H \cdot L \cdot B}{1024^2}$$

For a standard 32-layer model at $128\text{k}$ context tokens in FP16:
$$M_{\text{kv\_cache}} = \frac{2 \cdot 32 \cdot 32 \cdot 128 \cdot 131,072 \cdot 2}{1,048,576} = 65,536\text{ MB} = 64.0\text{ GB}$$

The KV-cache dwarfs the underlying weights ($14\text{GB}$ for 7B Q4). Static tools that only check weight size trigger fatal kernel OOM panics.

---

## 2. Dynamic Memory Horizon & Headroom Projection

`VRAMProjector` samples memory allocation in a circular ring buffer and computes instantaneous growth rate:

$$\frac{dM}{dt} = \frac{M_{\text{newest}} - M_{\text{oldest}}}{t_{\text{newest}} - t_{\text{oldest}}}$$

Time-to-exhaustion headroom:

$$T_{\text{headroom}} = \frac{M_{\text{capacity}} \cdot W_{\text{eviction}} - M_{\text{current}}}{\max(0.001, \frac{dM}{dt})}$$

When $T_{\text{headroom}} < 5.0\text{s}$ or allocated VRAM exceeds $85\%$ capacity, Apex Rig signals `ContextFabricAdapter` to evict cold KV pages to host DRAM and CXL/NVMe storage tiers.
