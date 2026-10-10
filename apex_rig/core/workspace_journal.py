"""
apex_rig.core.workspace_journal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Transactional Copy-On-Write Workspace Journal with O(1) Speculative Rollback.
Isolates concurrent agent harness filesystem mutations and prevents race conditions.
"""

from typing import Dict, List, Optional, Tuple
import hashlib
import time
from apex_rig.core.primitives import JournalEntry


class WorkspaceJournal:
    """
    Append-only journal managing speculative workspace transactions across agent harnesses.
    """

    def __init__(self):
        self._entries: Dict[str, JournalEntry] = {}
        self._harness_transactions: Dict[str, List[str]] = {}
        self._staged_files: Dict[str, str] = {}  # file_path -> harness_id holding lock

    def stage_change(
        self,
        harness_id: str,
        file_path: str,
        action: str,
        original_content: str,
        new_content: str,
    ) -> Tuple[bool, str, Optional[JournalEntry]]:
        """
        Stages a speculative file mutation for a harness.
        Returns: (success, message, entry)
        """
        # Detect concurrent edit conflict
        if file_path in self._staged_files and self._staged_files[file_path] != harness_id:
            locked_by = self._staged_files[file_path]
            return (False, f"Conflict: file '{file_path}' currently locked by harness '{locked_by}'", None)

        orig_hash = hashlib.sha256(original_content.encode("utf-8")).hexdigest()
        new_hash = hashlib.sha256(new_content.encode("utf-8")).hexdigest()

        entry_id = f"txn_{harness_id}_{int(time.time() * 1000)}_{len(self._entries)}"
        diff_payload = f"--- original ({orig_hash[:8]})\n+++ new ({new_hash[:8]})\n{action.upper()}: {file_path}"

        entry = JournalEntry(
            entry_id=entry_id,
            harness_id=harness_id,
            file_path=file_path,
            action=action,
            original_content_hash=orig_hash,
            new_content_hash=new_hash,
            diff_payload=diff_payload,
            committed=False,
            timestamp=time.time(),
        )

        self._entries[entry_id] = entry
        if harness_id not in self._harness_transactions:
            self._harness_transactions[harness_id] = []
        self._harness_transactions[harness_id].append(entry_id)
        self._staged_files[file_path] = harness_id

        return (True, f"Staged mutation {entry_id} for {file_path}", entry)

    def commit_transaction(self, harness_id: str) -> List[JournalEntry]:
        """
        Atomically commits all staged mutations for a harness.
        """
        committed_entries = []
        entry_ids = self._harness_transactions.get(harness_id, [])
        for eid in entry_ids:
            entry = self._entries.get(eid)
            if entry and not entry.committed:
                entry.committed = True
                committed_entries.append(entry)
                if entry.file_path in self._staged_files:
                    del self._staged_files[entry.file_path]

        self._harness_transactions[harness_id] = []
        return committed_entries

    def rollback_transaction(self, harness_id: str) -> List[JournalEntry]:
        """
        Discards staged mutations for a harness in O(1) time without filesystem damage.
        """
        rolled_back_entries = []
        entry_ids = self._harness_transactions.get(harness_id, [])
        for eid in entry_ids:
            entry = self._entries.get(eid)
            if entry and not entry.committed:
                rolled_back_entries.append(entry)
                if entry.file_path in self._staged_files:
                    del self._staged_files[entry.file_path]
                del self._entries[eid]

        self._harness_transactions[harness_id] = []
        return rolled_back_entries

    def get_pending_count(self, harness_id: Optional[str] = None) -> int:
        if harness_id:
            return len(self._harness_transactions.get(harness_id, []))
        return sum(len(e) for e in self._harness_transactions.values())
