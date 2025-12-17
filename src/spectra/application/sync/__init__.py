"""
Sync Module - Orchestration of synchronization between markdown and issue tracker.
"""

from .audit import AuditEntry, AuditTrail, AuditTrailRecorder, create_audit_trail
from .backup import (
    Backup,
    BackupManager,
    IssueSnapshot,
    RestoreOperation,
    RestoreResult,
    create_pre_sync_backup,
    restore_from_backup,
)
from .conflict import (
    Conflict,
    ConflictDetector,
    ConflictReport,
    ConflictResolution,
    ConflictResolver,
    ConflictType,
    FieldSnapshot,
    ResolutionStrategy,
    SnapshotStore,
    StorySnapshot,
    SyncSnapshot,
    create_snapshot_from_sync,
)
from .diff import (
    DiffCalculator,
    DiffFormatter,
    DiffResult,
    FieldDiff,
    IssueDiff,
    compare_backup_to_current,
)
from .incremental import (
    ChangeDetectionResult,
    ChangeTracker,
    IncrementalSyncStats,
    StoryFingerprint,
    compute_story_hash,
    stories_differ,
)
from .links import (
    LinkChange,
    LinkSyncOrchestrator,
    LinkSyncResult,
)
from .multi_epic import (
    EpicSyncResult,
    MultiEpicSyncOrchestrator,
    MultiEpicSyncResult,
)
from .orchestrator import FailedOperation, SyncOrchestrator, SyncResult
from .reverse_sync import (
    ChangeDetail,
    PullChanges,
    PullResult,
    ReverseSyncOrchestrator,
)
from .state import OperationRecord, StateStore, SyncPhase, SyncState


# Parallel operations (optional, requires aiohttp)
try:
    from .parallel import (
        ParallelSyncOperations,
        ParallelSyncResult,
        is_parallel_available,
    )

    PARALLEL_AVAILABLE = True
except ImportError:
    PARALLEL_AVAILABLE = False

__all__ = [
    # Parallel Operations
    "PARALLEL_AVAILABLE",
    "AuditEntry",
    # Audit trail
    "AuditTrail",
    "AuditTrailRecorder",
    # Backup & Restore
    "Backup",
    "BackupManager",
    "ChangeDetail",
    "ChangeDetectionResult",
    "ChangeTracker",
    "Conflict",
    "ConflictDetector",
    "ConflictReport",
    "ConflictResolution",
    "ConflictResolver",
    # Conflict Detection
    "ConflictType",
    "DiffCalculator",
    "DiffFormatter",
    # Diff
    "DiffResult",
    "EpicSyncResult",
    "FailedOperation",
    "FieldDiff",
    "FieldSnapshot",
    "IncrementalSyncStats",
    "IssueDiff",
    "IssueSnapshot",
    "LinkChange",
    # Link Sync
    "LinkSyncOrchestrator",
    "LinkSyncResult",
    # Multi-Epic Sync
    "MultiEpicSyncOrchestrator",
    "MultiEpicSyncResult",
    "OperationRecord",
    "PullChanges",
    "PullResult",
    "ResolutionStrategy",
    "RestoreOperation",
    "RestoreResult",
    # Reverse Sync (Pull)
    "ReverseSyncOrchestrator",
    "SnapshotStore",
    "StateStore",
    # Incremental Sync
    "StoryFingerprint",
    "StorySnapshot",
    "SyncOrchestrator",
    "SyncPhase",
    "SyncResult",
    "SyncSnapshot",
    "SyncState",
    "compare_backup_to_current",
    "compute_story_hash",
    "create_audit_trail",
    "create_pre_sync_backup",
    "create_snapshot_from_sync",
    "restore_from_backup",
    "stories_differ",
]
