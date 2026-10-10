"""
apex_rig.core.radix_trie
~~~~~~~~~~~~~~~~~~~~~~~~

Compressed Prefix Radix Trie for multi-harness context deduplication.
Caches and references common prefixes (system instructions, repository maps, file trees)
to eliminate redundant token ingestion across parallel agent harnesses.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import hashlib


@dataclass
class RadixNode:
    segment: str
    children: Dict[str, "RadixNode"] = field(default_factory=dict)
    ref_count: int = 0
    token_count: int = 0
    node_id: str = ""

    def __post_init__(self):
        if not self.node_id:
            self.node_id = hashlib.sha256(self.segment.encode("utf-8")).hexdigest()[:16]


class PrefixRadixTrie:
    """
    In-memory compressed Radix Trie tracking prefix deduplication across harnesses.
    """

    def __init__(self, avg_chars_per_token: float = 4.0):
        self.root = RadixNode(segment="")
        self.avg_chars_per_token = avg_chars_per_token
        self._total_registered_prompts = 0
        self._total_raw_tokens = 0
        self._total_deduplicated_tokens = 0

    def register_prefix(self, prefix_text: str, harness_id: str) -> Tuple[str, int, int]:
        """
        Registers a context prefix for a harness.
        Returns: (prefix_id, shared_token_count, unique_token_count)
        """
        if not prefix_text:
            return ("", 0, 0)

        raw_tokens = max(1, int(len(prefix_text) / self.avg_chars_per_token))
        self._total_registered_prompts += 1
        self._total_raw_tokens += raw_tokens

        # Segment by lines or paragraphs for structural alignment
        segments = [line + "\n" for line in prefix_text.splitlines(keepends=False)]
        if not segments:
            segments = [prefix_text]

        curr = self.root
        shared_tokens = 0
        is_shared = True

        for seg in segments:
            seg_tokens = max(1, int(len(seg) / self.avg_chars_per_token))
            if seg in curr.children:
                curr = curr.children[seg]
                curr.ref_count += 1
                if is_shared and curr.ref_count > 1:
                    shared_tokens += seg_tokens
            else:
                is_shared = False
                new_node = RadixNode(segment=seg, token_count=seg_tokens, ref_count=1)
                curr.children[seg] = new_node
                curr = new_node

        unique_tokens = max(0, raw_tokens - shared_tokens)
        self._total_deduplicated_tokens += (raw_tokens - shared_tokens)

        prefix_hash = hashlib.sha256(prefix_text.encode("utf-8")).hexdigest()[:16]
        return (prefix_hash, shared_tokens, unique_tokens)

    def release_prefix(self, prefix_text: str) -> None:
        """
        Decrements reference count across the path when a harness finishes.
        """
        if not prefix_text:
            return

        segments = [line + "\n" for line in prefix_text.splitlines(keepends=False)]
        curr = self.root
        for seg in segments:
            if seg in curr.children:
                curr = curr.children[seg]
                curr.ref_count = max(0, curr.ref_count - 1)

    def get_deduplication_ratio(self) -> float:
        """
        Calculates aggregate token savings ratio across all registered harnesses.
        Formula: 1.0 - (deduplicated_tokens / raw_tokens)
        """
        if self._total_raw_tokens == 0:
            return 0.0
        return max(0.0, 1.0 - (self._total_deduplicated_tokens / self._total_raw_tokens))

    def get_metrics(self) -> Dict[str, float]:
        ratio = self.get_deduplication_ratio()
        return {
            "total_prompts": self._total_registered_prompts,
            "total_raw_tokens": self._total_raw_tokens,
            "deduplicated_tokens": self._total_deduplicated_tokens,
            "tokens_saved": max(0, self._total_raw_tokens - self._total_deduplicated_tokens),
            "savings_percentage": ratio * 100.0,
        }
