"""
Sync Module - Orchestration of synchronization between markdown and issue tracker.
"""

from .orchestrator import SyncOrchestrator, SyncResult, FailedOperation
from .state import SyncState, StateStore, SyncPhase, OperationRecord
from .audit import AuditTrail, AuditEntry, AuditTrailRecorder, create_audit_trail
from .backup import (
    Backup,
    BackupManager,
    IssueSnapshot,
    RestoreResult,
    RestoreOperation,
    create_pre_sync_backup,
    restore_from_backup,
)

__all__ = [
    "SyncOrchestrator",
    "SyncResult",
    "FailedOperation",
    "SyncState",
    "StateStore",
    "SyncPhase",
    "OperationRecord",
    # Audit trail
    "AuditTrail",
    "AuditEntry",
    "AuditTrailRecorder",
    "create_audit_trail",
    # Backup & Restore
    "Backup",
    "BackupManager",
    "IssueSnapshot",
    "RestoreResult",
    "RestoreOperation",
    "create_pre_sync_backup",
    "restore_from_backup",
]

