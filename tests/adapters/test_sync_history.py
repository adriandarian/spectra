"""
Tests for sync history store adapters.

Tests the SyncHistoryPort implementation for:
- SQLiteSyncHistoryStore (SQLite database)
"""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from spectra.adapters.sync_history import (
    SQLiteSyncHistoryStore,
    generate_change_id,
    generate_entry_id,
)
from spectra.core.ports.sync_history import (
    ChangeRecord,
    HistoryQuery,
    SyncHistoryEntry,
    SyncOutcome,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_entry() -> SyncHistoryEntry:
    """Create a sample sync history entry for testing."""
    return SyncHistoryEntry(
        entry_id=generate_entry_id(),
        session_id="session-123",
        markdown_path="/path/to/stories.md",
        epic_key="PROJ-100",
        tracker_type="jira",
        outcome=SyncOutcome.SUCCESS,
        started_at=datetime.now() - timedelta(minutes=5),
        completed_at=datetime.now(),
        duration_seconds=300.0,
        operations_total=10,
        operations_succeeded=8,
        operations_failed=1,
        operations_skipped=1,
        dry_run=False,
        user="testuser",
        config_snapshot={"tracker": "jira", "epic": "PROJ-100"},
        changes_snapshot=[{"type": "create", "id": "PROJ-101"}],
        metadata={"version": "1.0"},
    )


@pytest.fixture
def multiple_entries() -> list[SyncHistoryEntry]:
    """Create multiple entries for testing queries."""
    base_time = datetime.now()
    entries = []

    # Entry 0: success, jira, PROJ-100
    entries.append(
        SyncHistoryEntry(
            entry_id=generate_entry_id(),
            session_id="session-0",
            markdown_path="/path/to/stories.md",
            epic_key="PROJ-100",
            tracker_type="jira",
            outcome=SyncOutcome.SUCCESS,
            started_at=base_time - timedelta(hours=5),
            completed_at=base_time - timedelta(hours=4),
            duration_seconds=3600.0,
            operations_total=20,
            operations_succeeded=18,
            operations_failed=2,
            dry_run=False,
        )
    )

    # Entry 1: failed, github, PROJ-100
    entries.append(
        SyncHistoryEntry(
            entry_id=generate_entry_id(),
            session_id="session-1",
            markdown_path="/path/to/stories.md",
            epic_key="PROJ-100",
            tracker_type="github",
            outcome=SyncOutcome.FAILED,
            started_at=base_time - timedelta(hours=3),
            completed_at=base_time - timedelta(hours=2),
            duration_seconds=3600.0,
            operations_total=15,
            operations_succeeded=0,
            operations_failed=15,
            dry_run=False,
            error_message="API error",
        )
    )

    # Entry 2: success, jira, PROJ-200
    entries.append(
        SyncHistoryEntry(
            entry_id=generate_entry_id(),
            session_id="session-2",
            markdown_path="/path/to/other.md",
            epic_key="PROJ-200",
            tracker_type="jira",
            outcome=SyncOutcome.SUCCESS,
            started_at=base_time - timedelta(hours=2),
            completed_at=base_time - timedelta(hours=1),
            duration_seconds=3600.0,
            operations_total=25,
            operations_succeeded=25,
            operations_failed=0,
            dry_run=False,
        )
    )

    # Entry 3: dry_run, linear, PROJ-300
    entries.append(
        SyncHistoryEntry(
            entry_id=generate_entry_id(),
            session_id="session-3",
            markdown_path="/path/to/stories.md",
            epic_key="PROJ-300",
            tracker_type="linear",
            outcome=SyncOutcome.DRY_RUN,
            started_at=base_time - timedelta(hours=1),
            completed_at=base_time - timedelta(minutes=30),
            duration_seconds=1800.0,
            operations_total=10,
            operations_succeeded=10,
            operations_failed=0,
            dry_run=True,
        )
    )

    # Entry 4: partial, jira, PROJ-100
    entries.append(
        SyncHistoryEntry(
            entry_id=generate_entry_id(),
            session_id="session-4",
            markdown_path="/path/to/stories.md",
            epic_key="PROJ-100",
            tracker_type="jira",
            outcome=SyncOutcome.PARTIAL,
            started_at=base_time - timedelta(minutes=30),
            completed_at=base_time,
            duration_seconds=1800.0,
            operations_total=30,
            operations_succeeded=20,
            operations_failed=10,
            dry_run=False,
        )
    )

    return entries


@pytest.fixture
def sample_changes(sample_entry: SyncHistoryEntry) -> list[ChangeRecord]:
    """Create sample change records for testing."""
    return [
        ChangeRecord(
            change_id=generate_change_id(),
            entry_id=sample_entry.entry_id,
            operation_type="create",
            entity_type="story",
            entity_id="PROJ-101",
            story_id="US-1",
            timestamp=datetime.now() - timedelta(minutes=4),
        ),
        ChangeRecord(
            change_id=generate_change_id(),
            entry_id=sample_entry.entry_id,
            operation_type="update",
            entity_type="story",
            entity_id="PROJ-102",
            story_id="US-2",
            field_name="description",
            old_value="Old description",
            new_value="New description",
            timestamp=datetime.now() - timedelta(minutes=3),
        ),
        ChangeRecord(
            change_id=generate_change_id(),
            entry_id=sample_entry.entry_id,
            operation_type="create",
            entity_type="subtask",
            entity_id="PROJ-103",
            story_id="US-1",
            timestamp=datetime.now() - timedelta(minutes=2),
        ),
    ]


@pytest.fixture
def sqlite_store(tmp_path: Path) -> SQLiteSyncHistoryStore:
    """Create a temporary SQLite history store."""
    db_path = tmp_path / "test_history.db"
    store = SQLiteSyncHistoryStore(db_path=db_path)
    yield store
    store.close()


# =============================================================================
# Test SQLiteSyncHistoryStore
# =============================================================================


class TestSQLiteSyncHistoryStore:
    """Tests for SQLiteSyncHistoryStore."""

    def test_record_and_get_entry(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        sample_entry: SyncHistoryEntry,
    ) -> None:
        """Test recording and retrieving a history entry."""
        sqlite_store.record(sample_entry)
        loaded = sqlite_store.get_entry(sample_entry.entry_id)

        assert loaded is not None
        assert loaded.entry_id == sample_entry.entry_id
        assert loaded.session_id == sample_entry.session_id
        assert loaded.markdown_path == sample_entry.markdown_path
        assert loaded.epic_key == sample_entry.epic_key
        assert loaded.tracker_type == sample_entry.tracker_type
        assert loaded.outcome == sample_entry.outcome
        assert loaded.operations_total == sample_entry.operations_total
        assert loaded.operations_succeeded == sample_entry.operations_succeeded
        assert loaded.operations_failed == sample_entry.operations_failed
        assert loaded.dry_run == sample_entry.dry_run
        assert loaded.user == sample_entry.user
        assert loaded.config_snapshot == sample_entry.config_snapshot
        assert loaded.metadata == sample_entry.metadata

    def test_get_nonexistent_entry(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
    ) -> None:
        """Test getting a non-existent entry returns None."""
        loaded = sqlite_store.get_entry("nonexistent")
        assert loaded is None

    def test_record_changes(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        sample_entry: SyncHistoryEntry,
        sample_changes: list[ChangeRecord],
    ) -> None:
        """Test recording change records."""
        sqlite_store.record(sample_entry)
        sqlite_store.record_changes(sample_changes)

        changes = sqlite_store.get_changes(sample_entry.entry_id)
        assert len(changes) == 3
        assert changes[0].operation_type == "create"
        assert changes[1].operation_type == "update"
        assert changes[1].old_value == "Old description"
        assert changes[1].new_value == "New description"

    def test_record_single_change(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        sample_entry: SyncHistoryEntry,
    ) -> None:
        """Test recording a single change record."""
        sqlite_store.record(sample_entry)

        change = ChangeRecord(
            change_id=generate_change_id(),
            entry_id=sample_entry.entry_id,
            operation_type="delete",
            entity_type="subtask",
            entity_id="PROJ-104",
            story_id="US-3",
        )
        sqlite_store.record_change(change)

        changes = sqlite_store.get_changes(sample_entry.entry_id)
        assert len(changes) == 1
        assert changes[0].operation_type == "delete"

    def test_query_all(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        multiple_entries: list[SyncHistoryEntry],
    ) -> None:
        """Test querying all entries."""
        for entry in multiple_entries:
            sqlite_store.record(entry)

        results = sqlite_store.query(HistoryQuery())
        assert len(results) == len(multiple_entries)

    def test_query_by_epic_key(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        multiple_entries: list[SyncHistoryEntry],
    ) -> None:
        """Test filtering by epic key."""
        for entry in multiple_entries:
            sqlite_store.record(entry)

        query = HistoryQuery(epic_key="PROJ-100")
        results = sqlite_store.query(query)
        assert len(results) == 3  # Entries 0, 1, 4

        for result in results:
            assert result.epic_key == "PROJ-100"

    def test_query_by_tracker_type(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        multiple_entries: list[SyncHistoryEntry],
    ) -> None:
        """Test filtering by tracker type."""
        for entry in multiple_entries:
            sqlite_store.record(entry)

        query = HistoryQuery(tracker_type="jira")
        results = sqlite_store.query(query)
        assert len(results) == 3  # Entries 0, 2, 4

        for result in results:
            assert result.tracker_type == "jira"

    def test_query_by_outcome(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        multiple_entries: list[SyncHistoryEntry],
    ) -> None:
        """Test filtering by outcome."""
        for entry in multiple_entries:
            sqlite_store.record(entry)

        query = HistoryQuery(outcomes=["success"])
        results = sqlite_store.query(query)
        assert len(results) == 2  # Entries 0, 2

        for result in results:
            assert result.outcome == SyncOutcome.SUCCESS

    def test_query_by_dry_run(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        multiple_entries: list[SyncHistoryEntry],
    ) -> None:
        """Test filtering by dry_run flag."""
        for entry in multiple_entries:
            sqlite_store.record(entry)

        query = HistoryQuery(dry_run=True)
        results = sqlite_store.query(query)
        assert len(results) == 1  # Entry 3

        assert results[0].dry_run is True

    def test_query_by_time_range(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        multiple_entries: list[SyncHistoryEntry],
    ) -> None:
        """Test filtering by time range."""
        for entry in multiple_entries:
            sqlite_store.record(entry)

        # Get entries completed after 45 minutes ago (should be entries 3 and 4)
        # Entry 2: completed_at = base_time - 1 hour (excluded)
        # Entry 3: completed_at = base_time - 30 minutes (included)
        # Entry 4: completed_at = base_time (included)
        cutoff = datetime.now() - timedelta(minutes=45)
        query = HistoryQuery(after=cutoff)
        results = sqlite_store.query(query)
        assert len(results) == 2  # Entries 3, 4

    def test_query_with_limit(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        multiple_entries: list[SyncHistoryEntry],
    ) -> None:
        """Test query with limit."""
        for entry in multiple_entries:
            sqlite_store.record(entry)

        query = HistoryQuery(limit=2)
        results = sqlite_store.query(query)
        assert len(results) == 2

    def test_query_with_pagination(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        multiple_entries: list[SyncHistoryEntry],
    ) -> None:
        """Test query with pagination."""
        for entry in multiple_entries:
            sqlite_store.record(entry)

        query = HistoryQuery(limit=2, offset=2, order_desc=True)
        results = sqlite_store.query(query)
        assert len(results) == 2

    def test_count(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        multiple_entries: list[SyncHistoryEntry],
    ) -> None:
        """Test counting entries."""
        for entry in multiple_entries:
            sqlite_store.record(entry)

        assert sqlite_store.count() == len(multiple_entries)
        assert sqlite_store.count(HistoryQuery(tracker_type="jira")) == 3
        assert sqlite_store.count(HistoryQuery(outcomes=["failed"])) == 1

    def test_get_rollbackable_changes(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        sample_entry: SyncHistoryEntry,
        sample_changes: list[ChangeRecord],
    ) -> None:
        """Test getting rollbackable changes."""
        sqlite_store.record(sample_entry)
        sqlite_store.record_changes(sample_changes)

        rollbackable = sqlite_store.get_rollbackable_changes(sample_entry.entry_id)
        assert len(rollbackable) == 3

        # All changes should not be rolled back yet
        for change in rollbackable:
            assert change.rolled_back is False

    def test_mark_rolled_back(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        sample_entry: SyncHistoryEntry,
        sample_changes: list[ChangeRecord],
    ) -> None:
        """Test marking changes as rolled back."""
        sqlite_store.record(sample_entry)
        sqlite_store.record_changes(sample_changes)

        rollback_entry_id = generate_entry_id()
        count = sqlite_store.mark_rolled_back(
            sample_entry.entry_id,
            rollback_entry_id,
        )
        assert count == 3

        # Verify changes are marked
        changes = sqlite_store.get_changes(sample_entry.entry_id)
        for change in changes:
            assert change.rolled_back is True
            assert change.rollback_entry_id == rollback_entry_id

        # Verify no more rollbackable changes
        rollbackable = sqlite_store.get_rollbackable_changes(sample_entry.entry_id)
        assert len(rollbackable) == 0

    def test_mark_specific_changes_rolled_back(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        sample_entry: SyncHistoryEntry,
        sample_changes: list[ChangeRecord],
    ) -> None:
        """Test marking specific changes as rolled back."""
        sqlite_store.record(sample_entry)
        sqlite_store.record_changes(sample_changes)

        rollback_entry_id = generate_entry_id()
        change_ids = [sample_changes[0].change_id, sample_changes[1].change_id]

        count = sqlite_store.mark_rolled_back(
            sample_entry.entry_id,
            rollback_entry_id,
            change_ids,
        )
        assert count == 2

        rollbackable = sqlite_store.get_rollbackable_changes(sample_entry.entry_id)
        assert len(rollbackable) == 1  # Only the third change remains

    def test_get_statistics(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        multiple_entries: list[SyncHistoryEntry],
    ) -> None:
        """Test getting aggregated statistics."""
        for entry in multiple_entries:
            sqlite_store.record(entry)

        stats = sqlite_store.get_statistics()

        assert stats.total_syncs == 5
        assert stats.successful_syncs == 2
        assert stats.failed_syncs == 1
        assert stats.partial_syncs == 1
        assert stats.dry_run_syncs == 1
        assert stats.total_operations == 100  # Sum of all operations
        assert stats.total_duration_seconds > 0
        assert stats.average_duration_seconds > 0

        # Check breakdowns
        assert "jira" in stats.syncs_by_tracker
        assert stats.syncs_by_tracker["jira"] == 3
        assert "PROJ-100" in stats.syncs_by_epic
        assert stats.syncs_by_epic["PROJ-100"] == 3

    def test_get_statistics_with_filter(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        multiple_entries: list[SyncHistoryEntry],
    ) -> None:
        """Test getting statistics with a filter."""
        for entry in multiple_entries:
            sqlite_store.record(entry)

        query = HistoryQuery(tracker_type="jira")
        stats = sqlite_store.get_statistics(query)

        assert stats.total_syncs == 3
        assert stats.successful_syncs == 2
        assert stats.partial_syncs == 1

    def test_get_velocity(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        multiple_entries: list[SyncHistoryEntry],
    ) -> None:
        """Test getting velocity metrics."""
        for entry in multiple_entries:
            sqlite_store.record(entry)

        end = datetime.now()
        start = end - timedelta(days=7)
        metrics = sqlite_store.get_velocity(start, end, interval_days=1)

        assert len(metrics) == 7  # 7 days
        # Most recent day should have activity
        assert metrics[-1].total_syncs > 0

    def test_get_recent_activity(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        multiple_entries: list[SyncHistoryEntry],
    ) -> None:
        """Test getting recent activity."""
        for entry in multiple_entries:
            sqlite_store.record(entry)

        recent = sqlite_store.get_recent_activity(days=7, limit=10)
        assert len(recent) == 5  # All entries are within 7 days

    def test_get_latest(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        multiple_entries: list[SyncHistoryEntry],
    ) -> None:
        """Test getting the latest entry."""
        for entry in multiple_entries:
            sqlite_store.record(entry)

        latest = sqlite_store.get_latest()
        assert latest is not None
        # Entry 4 has the most recent completed_at
        assert latest.session_id == "session-4"

    def test_get_latest_by_epic(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        multiple_entries: list[SyncHistoryEntry],
    ) -> None:
        """Test getting the latest entry for a specific epic."""
        for entry in multiple_entries:
            sqlite_store.record(entry)

        latest = sqlite_store.get_latest(epic_key="PROJ-200")
        assert latest is not None
        assert latest.epic_key == "PROJ-200"
        assert latest.session_id == "session-2"

    def test_get_last_successful(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        multiple_entries: list[SyncHistoryEntry],
    ) -> None:
        """Test getting the last successful sync."""
        for entry in multiple_entries:
            sqlite_store.record(entry)

        last_success = sqlite_store.get_last_successful(epic_key="PROJ-100")
        assert last_success is not None
        assert last_success.outcome == SyncOutcome.SUCCESS
        assert last_success.session_id == "session-0"

    def test_delete_before(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        multiple_entries: list[SyncHistoryEntry],
    ) -> None:
        """Test deleting old entries."""
        for entry in multiple_entries:
            sqlite_store.record(entry)

        # Entry 0: completed_at = base_time - 4 hours
        # Entry 1: completed_at = base_time - 2 hours
        # Entry 2: completed_at = base_time - 1 hour
        # Entry 3: completed_at = base_time - 30 minutes
        # Entry 4: completed_at = base_time
        # Cutoff at 3.5 hours should only delete Entry 0
        cutoff = datetime.now() - timedelta(hours=3, minutes=30)
        deleted = sqlite_store.delete_before(cutoff)

        # Entry 0 should be deleted (completed 4 hours ago)
        assert deleted == 1
        assert sqlite_store.count() == 4

    def test_info(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        sample_entry: SyncHistoryEntry,
        sample_changes: list[ChangeRecord],
    ) -> None:
        """Test getting store info."""
        sqlite_store.record(sample_entry)
        sqlite_store.record_changes(sample_changes)

        info = sqlite_store.info()

        assert info.backend == "sqlite"
        assert info.entry_count == 1
        assert info.change_count == 3
        assert info.storage_size_bytes is not None
        assert info.storage_size_bytes > 0
        assert info.oldest_entry is not None
        assert info.newest_entry is not None

    def test_vacuum(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        sample_entry: SyncHistoryEntry,
    ) -> None:
        """Test vacuum operation."""
        sqlite_store.record(sample_entry)

        # Delete the entry
        sqlite_store.delete_before(datetime.now() + timedelta(days=1))

        # Should not raise
        sqlite_store.vacuum()

    def test_checkpoint(
        self,
        sqlite_store: SQLiteSyncHistoryStore,
        sample_entry: SyncHistoryEntry,
    ) -> None:
        """Test WAL checkpoint operation."""
        sqlite_store.record(sample_entry)

        # Should not raise
        sqlite_store.checkpoint()

    def test_context_manager(
        self,
        tmp_path: Path,
        sample_entry: SyncHistoryEntry,
    ) -> None:
        """Test using store as context manager."""
        db_path = tmp_path / "context_test.db"
        with SQLiteSyncHistoryStore(db_path=db_path) as store:
            store.record(sample_entry)
            loaded = store.get_entry(sample_entry.entry_id)
            assert loaded is not None


# =============================================================================
# Test Helper Functions
# =============================================================================


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_generate_entry_id(self) -> None:
        """Test entry ID generation."""
        id1 = generate_entry_id()
        id2 = generate_entry_id()

        assert id1.startswith("hist-")
        assert id2.startswith("hist-")
        assert id1 != id2
        assert len(id1) == 17  # "hist-" + 12 hex chars

    def test_generate_change_id(self) -> None:
        """Test change ID generation."""
        id1 = generate_change_id()
        id2 = generate_change_id()

        assert id1.startswith("chg-")
        assert id2.startswith("chg-")
        assert id1 != id2
        assert len(id1) == 16  # "chg-" + 12 hex chars


# =============================================================================
# Test Data Classes
# =============================================================================


class TestDataClasses:
    """Tests for data classes."""

    def test_sync_history_entry_to_dict(
        self,
        sample_entry: SyncHistoryEntry,
    ) -> None:
        """Test SyncHistoryEntry.to_dict()."""
        data = sample_entry.to_dict()

        assert data["entry_id"] == sample_entry.entry_id
        assert data["session_id"] == sample_entry.session_id
        assert data["outcome"] == "success"
        assert "started_at" in data
        assert "completed_at" in data

    def test_sync_history_entry_from_dict(
        self,
        sample_entry: SyncHistoryEntry,
    ) -> None:
        """Test SyncHistoryEntry.from_dict()."""
        data = sample_entry.to_dict()
        loaded = SyncHistoryEntry.from_dict(data)

        assert loaded.entry_id == sample_entry.entry_id
        assert loaded.session_id == sample_entry.session_id
        assert loaded.outcome == sample_entry.outcome

    def test_change_record_to_dict(
        self,
        sample_entry: SyncHistoryEntry,
    ) -> None:
        """Test ChangeRecord.to_dict()."""
        change = ChangeRecord(
            change_id="chg-123",
            entry_id=sample_entry.entry_id,
            operation_type="update",
            entity_type="story",
            entity_id="PROJ-101",
            story_id="US-1",
            field_name="description",
            old_value="old",
            new_value="new",
        )
        data = change.to_dict()

        assert data["change_id"] == "chg-123"
        assert data["operation_type"] == "update"
        assert data["old_value"] == "old"
        assert data["new_value"] == "new"

    def test_change_record_from_dict(self) -> None:
        """Test ChangeRecord.from_dict()."""
        data = {
            "change_id": "chg-456",
            "entry_id": "hist-123",
            "operation_type": "create",
            "entity_type": "subtask",
            "entity_id": "PROJ-102",
            "story_id": "US-2",
            "timestamp": datetime.now().isoformat(),
        }
        change = ChangeRecord.from_dict(data)

        assert change.change_id == "chg-456"
        assert change.operation_type == "create"
        assert change.rolled_back is False

    def test_sync_statistics_to_dict(self) -> None:
        """Test SyncStatistics.to_dict()."""
        from spectra.core.ports.sync_history import SyncStatistics

        stats = SyncStatistics(
            total_syncs=10,
            successful_syncs=8,
            failed_syncs=2,
            first_sync_at=datetime.now() - timedelta(days=30),
            last_sync_at=datetime.now(),
        )
        data = stats.to_dict()

        assert data["total_syncs"] == 10
        assert data["successful_syncs"] == 8
        assert "first_sync_at" in data
        assert "last_sync_at" in data

    def test_velocity_metrics_to_dict(self) -> None:
        """Test VelocityMetrics.to_dict()."""
        from spectra.core.ports.sync_history import VelocityMetrics

        metrics = VelocityMetrics(
            period_start=datetime.now() - timedelta(days=7),
            period_end=datetime.now(),
            total_syncs=5,
            successful_syncs=4,
        )
        data = metrics.to_dict()

        assert data["total_syncs"] == 5
        assert "period_start" in data
        assert "period_end" in data
