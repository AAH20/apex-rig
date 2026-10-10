"""
apex_rig.router.key_pooler
~~~~~~~~~~~~~~~~~~~~~~~~~~

Multi-account API key pooling and rate-limit evasion engine.
Rotates credentials, tracks RPM/TPM usage, and trips circuit breakers on 429 throttling.
"""

from typing import Dict, List, Optional
import time
from dataclasses import dataclass, field


@dataclass
class APIKeySlot:
    key_id: str
    provider: str
    api_key_redacted: str
    max_rpm: int = 60
    max_tpm: int = 100000
    current_rpm: int = 0
    current_tpm: int = 0
    consecutive_errors: int = 0
    is_cooling_down: bool = False
    cooldown_until: float = 0.0
    last_reset_time: float = field(default_factory=time.time)


class KeyPooler:
    """
    Intelligent credential balancer distributing requests across multiple accounts per provider.
    """

    def __init__(self, cooldown_duration_sec: float = 60.0):
        self._provider_keys: Dict[str, List[APIKeySlot]] = {}
        self.cooldown_duration_sec = cooldown_duration_sec

    def register_key(self, provider: str, key_id: str, api_key: str, max_rpm: int = 60) -> None:
        if provider not in self._provider_keys:
            self._provider_keys[provider] = []

        redacted = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "sk-****"
        slot = APIKeySlot(
            key_id=key_id,
            provider=provider,
            api_key_redacted=redacted,
            max_rpm=max_rpm,
        )
        self._provider_keys[provider].append(slot)

    def acquire_key(self, provider: str, requested_tokens: int = 500) -> Optional[APIKeySlot]:
        """
        Retrieves the least loaded, non-cooling-down key for a provider.
        """
        keys = self._provider_keys.get(provider, [])
        if not keys:
            return None

        now = time.time()
        best_slot = None
        min_load = 1e9

        for slot in keys:
            # Check window reset
            if now - slot.last_reset_time >= 60.0:
                slot.current_rpm = 0
                slot.current_tpm = 0
                slot.last_reset_time = now

            # Check cooldown expiration
            if slot.is_cooling_down and now >= slot.cooldown_until:
                slot.is_cooling_down = False
                slot.consecutive_errors = 0

            if slot.is_cooling_down:
                continue

            # Check capacity limits
            if slot.current_rpm >= slot.max_rpm or (slot.current_tpm + requested_tokens) > slot.max_tpm:
                continue

            load = slot.current_rpm / slot.max_rpm
            if load < min_load:
                min_load = load
                best_slot = slot

        if best_slot:
            best_slot.current_rpm += 1
            best_slot.current_tpm += requested_tokens

        return best_slot

    def record_outcome(self, key_id: str, provider: str, success: bool, is_rate_limited: bool = False) -> None:
        keys = self._provider_keys.get(provider, [])
        for slot in keys:
            if slot.key_id == key_id:
                if success:
                    slot.consecutive_errors = 0
                else:
                    slot.consecutive_errors += 1
                    if is_rate_limited or slot.consecutive_errors >= 3:
                        slot.is_cooling_down = True
                        slot.cooldown_until = time.time() + self.cooldown_duration_sec
                break

    def get_status(self) -> Dict[str, Dict[str, int]]:
        status = {}
        for prov, slots in self._provider_keys.items():
            active = sum(1 for s in slots if not s.is_cooling_down)
            cooling = sum(1 for s in slots if s.is_cooling_down)
            status[prov] = {"total_keys": len(slots), "active_keys": active, "cooling_down": cooling}
        return status
