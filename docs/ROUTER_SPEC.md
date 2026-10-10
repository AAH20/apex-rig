# Apex Rig: Cognitive Router & Model Arbitration Specification

---

## 1. Information-Theoretic Prompt Classification

Apex Rig evaluates prompt complexity using **Shannon Information Entropy** $H(X)$:

$$H(X) = -\sum_{i=1}^{K} P(w_i) \log_2 P(w_i)$$

Where:
- $w_i$ represents normalized token unigrams.
- $P(w_i)$ is the empirical word probability within the prompt payload.
- Lexical diversity modifier: $\lambda = \frac{|\text{unique words}|}{|\text{total words}|}$.
- Calibrated Entropy: $H_{\text{adj}} = H(X) \cdot (0.7 + 0.3 \lambda)$.

### Tri-Tier Dispatch Regime

| Metric Range | Target Tier | Typical Providers | Rationale |
| :--- | :--- | :--- | :--- |
| $H_{\text{adj}} \le 2.0$ | `LOCAL_SILICON` | Local Apple Silicon / Groq / Qwen-2.5 | Low token surprise; deterministic formatting, syntax check, or boilerplate. Zero dollar cost. |
| $2.0 < H_{\text{adj}} < 3.5$ | `COMMODITY_CLOUD` | DeepSeek-V3, Llama-3.3-70B | Moderate complexity; unit test generation, standard business logic. \$0.27–\$1.10/M tokens. |
| $H_{\text{adj}} \ge 3.5$ | `FRONTIER_CLOUD` | Claude 3.5 Sonnet, DeepSeek-R1, GPT-4o | High conceptual entropy; cross-system architecture, multi-file synthesis. \$3.00–\$15.00/M tokens. |

---

## 2. Pareto Cost-Latency Objective Function

Within each tier, models are ranked according to a multi-objective trade-off:

$$\text{Score}(M) = W_{\text{cost}} \cdot (1.0 - \hat{C}_M) + W_{\text{lat}} \cdot (1.0 - \hat{L}_M) - \mathbb{I}(C_M > B_{\text{task}}) \cdot \rho$$

Where:
- $\hat{C}_M \in [0, 1]$ is normalized token pricing.
- $\hat{L}_M \in [0, 1]$ is normalized average provider latency.
- $B_{\text{task}}$ is the task dollar budget constraint.
- $\rho = 2.0$ is the budget violation penalty.

---

## 3. Multi-Account Credential Pooling & Rate-Limit Evasion

`KeyPooler` maintains an active slot registry per provider:
- Enforces sliding-window Requests-Per-Minute (RPM) and Tokens-Per-Minute (TPM) ceilings.
- Automatically isolates keys upon HTTP 429 throttling for $60.0\text{s}$ cooldowns.
- Reroutes pending queues to secondary accounts without user intervention.
