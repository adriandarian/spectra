"""Tests for backup functionality."""

import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from md2jira.application.sync.backup import (
    Backup,
    BackupManager,
    IssueSnapshot,
    create_pre_sync_backup,
)
from md2jira.core.ports.issue_tracker import IssueData


class TestIssueSnapshot:
    """Tests for IssueSnapshot class."""
    
    def test_from_issue_data(self):
        """Should create snapshot from IssueData."""
        subtask = IssueData(
            key="PROJ-101",
            summary="Subtask 1",
            status="Open",
            issue_type="Sub-task",
        )
        issue = IssueData(
            key="PROJ-100",
            summary="Test Story",
            description={"type": "doc", "content": []},
            status="In Progress",
            issue_type="Story",
            assignee="user123",
            story_points=5.0,
            subtasks=[subtask],
        )
        
        snapshot = IssueSnapshot.from_issue_data(issue, comments_count=3)
        
        assert snapshot.key == "PROJ-100"
        assert snapshot.summary == "Test Story"
        assert snapshot.status == "In Progress"
        assert snapshot.story_points == 5.0
        assert snapshot.comments_count == 3
        assert len(snapshot.subtasks) == 1
        assert snapshot.subtasks[0].key == "PROJ-101"
    
    def test_to_dict_and_back(self):
        """Should serialize and deserialize correctly."""
        snapshot = IssueSnapshot(
            key="PROJ-100",
            summary="Test Story",
            description="Some description",
            status="Open",
            story_points=3.0,
            subtasks=[
                IssueSnapshot(
                    key="PROJ-101",
                    summary="Subtask",
                    status="Todo",
                )
            ],
        )
        
        data = snapshot.to_dict()
        restored = IssueSnapshot.from_dict(data)
        
        assert restored.key == snapshot.key
        assert restored.summary == snapshot.summary
        assert restored.story_points == snapshot.story_points
        assert len(restored.subtasks) == 1
        assert restored.subtasks[0].key == "PROJ-101"


class TestBackup:
    """Tests for Backup class."""
    
    def test_issue_count(self):
        """Should count issues correctly."""
        backup = Backup(
            backup_id="test123",
            epic_key="PROJ-1",
            markdown_path="/path/to/file.md",
            issues=[
                IssueSnapshot(key="PROJ-100", summary="Story 1"),
                IssueSnapshot(key="PROJ-200", summary="Story 2"),
            ],
        )
        
        assert backup.issue_count == 2
    
    def test_subtask_count(self):
        """Should count subtasks across all issues."""
        backup = Backup(
            backup_id="test123",
            epic_key="PROJ-1",
            markdown_path="/path/to/file.md",
            issues=[
                IssueSnapshot(
                    key="PROJ-100",
                    summary="Story 1",
                    subtasks=[
                        IssueSnapshot(key="PROJ-101", summary="Sub 1"),
                        IssueSnapshot(key="PROJ-102", summary="Sub 2"),
                    ],
                ),
                IssueSnapshot(
                    key="PROJ-200",
                    summary="Story 2",
                    subtasks=[
                        IssueSnapshot(key="PROJ-201", summary="Sub 3"),
                    ],
                ),
            ],
        )
        
        assert backup.subtask_count == 3
    
    def test_get_issue(self):
        """Should find issue by key."""
        backup = Backup(
            backup_id="test123",
            epic_key="PROJ-1",
            markdown_path="/path/to/file.md",
            issues=[
                IssueSnapshot(
                    key="PROJ-100",
                    summary="Story 1",
                    subtasks=[
                        IssueSnapshot(key="PROJ-101", summary="Sub 1"),
                    ],
                ),
            ],
        )
        
        # Find parent issue
        issue = backup.get_issue("PROJ-100")
        assert issue is not None
        assert issue.summary == "Story 1"
        
        # Find subtask
        subtask = backup.get_issue("PROJ-101")
        assert subtask is not None
        assert subtask.summary == "Sub 1"
        
        # Not found
        assert backup.get_issue("PROJ-999") is None
    
    def test_to_dict_and_back(self):
        """Should serialize and deserialize correctly."""
        backup = Backup(
            backup_id="test123",
            epic_key="PROJ-1",
            markdown_path="/path/to/file.md",
            issues=[
                IssueSnapshot(key="PROJ-100", summary="Story 1"),
            ],
            metadata={"trigger": "test"},
        )
        
        data = backup.to_dict()
        restored = Backup.from_dict(data)
        
        assert restored.backup_id == backup.backup_id
        assert restored.epic_key == backup.epic_key
        assert restored.markdown_path == backup.markdown_path
        assert len(restored.issues) == 1
        assert restored.metadata == {"trigger": "test"}


class TestBackupManager:
    """Tests for BackupManager class."""
    
    @pytest.fixture
    def backup_dir(self, tmp_path):
        """Create a temporary backup directory."""
        return tmp_path / "backups"
    
    @pytest.fixture
    def manager(self, backup_dir):
        """Create a BackupManager with temp directory."""
        return BackupManager(
            backup_dir=backup_dir,
            max_backups=3,
            retention_days=7,
        )
    
    @pytest.fixture
    def mock_tracker(self):
        """Create a mock tracker."""
        tracker = MagicMock()
        tracker.get_epic_children.return_value = [
            IssueData(
                key="PROJ-100",
                summary="Story 1",
                status="Open",
                issue_type="Story",
                subtasks=[
                    IssueData(key="PROJ-101", summary="Sub 1", status="Todo"),
                ],
            ),
            IssueData(
                key="PROJ-200",
                summary="Story 2",
                status="In Progress",
                issue_type="Story",
            ),
        ]
        tracker.get_issue_comments.return_value = [{"id": "1"}, {"id": "2"}]
        return tracker
    
    def test_create_backup(self, manager, mock_tracker, backup_dir):
        """Should create backup and save to disk."""
        backup = manager.create_backup(
            tracker=mock_tracker,
            epic_key="PROJ-1",
            markdown_path="/path/to/file.md",
            metadata={"test": True},
        )
        
        # Check backup properties
        assert backup.epic_key == "PROJ-1"
        assert backup.markdown_path == "/path/to/file.md"
        assert backup.issue_count == 2
        assert backup.metadata == {"test": True}
        
        # Check file was created
        epic_dir = backup_dir / "PROJ-1"
        assert epic_dir.exists()
        backup_files = list(epic_dir.glob("*.json"))
        assert len(backup_files) == 1
    
    def test_save_and_load_backup(self, manager, backup_dir):
        """Should save and load backup correctly."""
        backup = Backup(
            backup_id="test_backup_123",
            epic_key="PROJ-1",
            markdown_path="/path/to/file.md",
            issues=[
                IssueSnapshot(key="PROJ-100", summary="Story 1"),
            ],
        )
        
        # Save
        path = manager.save_backup(backup)
        assert path.exists()
        
        # Load
        loaded = manager.load_backup("test_backup_123", "PROJ-1")
        assert loaded is not None
        assert loaded.backup_id == backup.backup_id
        assert loaded.issue_count == 1
    
    def test_list_backups(self, manager, mock_tracker):
        """Should list all backups."""
        # Create multiple backups for different epics
        # Manager has max_backups=3 per epic, so within-epic cleanup applies
        manager.create_backup(mock_tracker, "PROJ-1", "/file1.md")
        manager.create_backup(mock_tracker, "PROJ-2", "/file2.md")
        manager.create_backup(mock_tracker, "PROJ-3", "/file3.md")
        
        # List all - should have 3 (one per epic)
        all_backups = manager.list_backups()
        assert len(all_backups) == 3
        
        # List by epic - each should have 1
        proj1_backups = manager.list_backups("PROJ-1")
        assert len(proj1_backups) == 1
        
        proj2_backups = manager.list_backups("PROJ-2")
        assert len(proj2_backups) == 1
    
    def test_get_latest_backup(self, manager, mock_tracker):
        """Should return most recent backup."""
        # Create backups with slight delay between them
        backup1 = manager.create_backup(mock_tracker, "PROJ-1", "/file1.md")
        backup2 = manager.create_backup(mock_tracker, "PROJ-1", "/file2.md")
        
        latest = manager.get_latest_backup("PROJ-1")
        assert latest is not None
        assert latest.backup_id == backup2.backup_id
    
    def test_delete_backup(self, manager, mock_tracker, backup_dir):
        """Should delete backup file."""
        backup = manager.create_backup(mock_tracker, "PROJ-1", "/file.md")
        
        # Verify exists
        assert len(manager.list_backups("PROJ-1")) == 1
        
        # Delete
        result = manager.delete_backup(backup.backup_id, "PROJ-1")
        assert result is True
        
        # Verify deleted
        assert len(manager.list_backups("PROJ-1")) == 0
    
    def test_cleanup_over_limit(self, backup_dir, mock_tracker):
        """Should cleanup backups over max limit."""
        # Create manager with max_backups=3
        manager = BackupManager(
            backup_dir=backup_dir,
            max_backups=3,
            retention_days=7,
        )
        
        # Create more than max_backups (3)
        created_backups = []
        for i in range(5):
            backup = manager.create_backup(mock_tracker, "PROJ-1", f"/file{i}.md")
            created_backups.append(backup)
        
        # After creating 5, cleanup should have kept only 3 most recent
        backups = manager.list_backups("PROJ-1")
        assert len(backups) == 3
        
        # The 3 kept should be the most recent ones
        backup_ids = {b["backup_id"] for b in backups}
        # Last 3 created should be kept
        assert created_backups[-1].backup_id in backup_ids
    
    def test_backup_id_generation(self, manager):
        """Should generate unique backup IDs."""
        # Generate multiple IDs rapidly
        ids = [manager._generate_backup_id("PROJ-1") for _ in range(10)]
        
        # All IDs should be unique (uses microseconds now)
        assert len(set(ids)) == 10
        
        # All IDs should contain epic key
        for id_ in ids:
            assert "PROJ-1" in id_


class TestCreatePreSyncBackup:
    """Tests for create_pre_sync_backup convenience function."""
    
    def test_creates_backup(self, tmp_path):
        """Should create backup with pre_sync metadata."""
        tracker = MagicMock()
        tracker.get_epic_children.return_value = [
            IssueData(key="PROJ-100", summary="Story 1", status="Open"),
        ]
        tracker.get_issue_comments.return_value = []
        
        backup = create_pre_sync_backup(
            tracker=tracker,
            epic_key="PROJ-1",
            markdown_path="/path/to/epic.md",
            backup_dir=tmp_path / "backups",
        )
        
        assert backup.epic_key == "PROJ-1"
        assert backup.metadata.get("trigger") == "pre_sync"
        assert backup.issue_count == 1

