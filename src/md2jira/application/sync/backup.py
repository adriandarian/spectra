"""
Backup Manager - Auto-backup Jira state before modifications.

Captures the current state of issues before sync operations,
allowing recovery if something goes wrong.
"""

import json
import logging
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.ports.issue_tracker import IssueTrackerPort, IssueData


logger = logging.getLogger(__name__)


@dataclass
class IssueSnapshot:
    """
    Snapshot of a single issue's state.
    
    Captures all mutable fields that could be modified during sync.
    """
    key: str
    summary: str
    description: Optional[Any] = None
    status: str = ""
    issue_type: str = ""
    assignee: Optional[str] = None
    story_points: Optional[float] = None
    subtasks: list["IssueSnapshot"] = field(default_factory=list)
    comments_count: int = 0
    captured_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "key": self.key,
            "summary": self.summary,
            "description": self.description,
            "status": self.status,
            "issue_type": self.issue_type,
            "assignee": self.assignee,
            "story_points": self.story_points,
            "subtasks": [st.to_dict() for st in self.subtasks],
            "comments_count": self.comments_count,
            "captured_at": self.captured_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "IssueSnapshot":
        """Create from dictionary."""
        subtasks = [cls.from_dict(st) for st in data.get("subtasks", [])]
        return cls(
            key=data["key"],
            summary=data.get("summary", ""),
            description=data.get("description"),
            status=data.get("status", ""),
            issue_type=data.get("issue_type", ""),
            assignee=data.get("assignee"),
            story_points=data.get("story_points"),
            subtasks=subtasks,
            comments_count=data.get("comments_count", 0),
            captured_at=data.get("captured_at", datetime.now().isoformat()),
        )
    
    @classmethod
    def from_issue_data(cls, issue: "IssueData", comments_count: int = 0) -> "IssueSnapshot":
        """Create snapshot from IssueData."""
        subtasks = [
            cls(
                key=st.key,
                summary=st.summary,
                description=st.description,
                status=st.status,
                issue_type=st.issue_type,
                assignee=st.assignee,
                story_points=st.story_points,
            )
            for st in issue.subtasks
        ]
        return cls(
            key=issue.key,
            summary=issue.summary,
            description=issue.description,
            status=issue.status,
            issue_type=issue.issue_type,
            assignee=issue.assignee,
            story_points=issue.story_points,
            subtasks=subtasks,
            comments_count=comments_count,
        )


@dataclass
class Backup:
    """
    Complete backup of Jira state before a sync operation.
    
    Contains snapshots of all issues that may be modified,
    along with metadata about when and why the backup was created.
    """
    backup_id: str
    epic_key: str
    markdown_path: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    issues: list[IssueSnapshot] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    
    @property
    def issue_count(self) -> int:
        """Total number of issues in backup."""
        return len(self.issues)
    
    @property
    def subtask_count(self) -> int:
        """Total number of subtasks across all issues."""
        return sum(len(issue.subtasks) for issue in self.issues)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "backup_id": self.backup_id,
            "epic_key": self.epic_key,
            "markdown_path": self.markdown_path,
            "created_at": self.created_at,
            "issues": [issue.to_dict() for issue in self.issues],
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Backup":
        """Create from dictionary."""
        issues = [IssueSnapshot.from_dict(i) for i in data.get("issues", [])]
        return cls(
            backup_id=data["backup_id"],
            epic_key=data["epic_key"],
            markdown_path=data.get("markdown_path", ""),
            created_at=data.get("created_at", datetime.now().isoformat()),
            issues=issues,
            metadata=data.get("metadata", {}),
        )
    
    def get_issue(self, issue_key: str) -> Optional[IssueSnapshot]:
        """Find an issue snapshot by key."""
        for issue in self.issues:
            if issue.key == issue_key:
                return issue
            # Check subtasks
            for subtask in issue.subtasks:
                if subtask.key == issue_key:
                    return subtask
        return None
    
    def summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            f"Backup ID: {self.backup_id}",
            f"Epic: {self.epic_key}",
            f"Created: {self.created_at}",
            f"Issues: {self.issue_count}",
            f"Subtasks: {self.subtask_count}",
        ]
        return "\n".join(lines)


class BackupManager:
    """
    Manages automatic backups of Jira state before sync operations.
    
    Features:
    - Auto-backup before sync (configurable)
    - Backup rotation with configurable retention
    - Backup listing and restoration helpers
    - JSON storage for easy inspection
    
    Default backup location: ~/.md2jira/backups/
    """
    
    DEFAULT_BACKUP_DIR = Path.home() / ".md2jira" / "backups"
    DEFAULT_MAX_BACKUPS = 10
    DEFAULT_RETENTION_DAYS = 30
    
    def __init__(
        self,
        backup_dir: Optional[Path] = None,
        max_backups: int = DEFAULT_MAX_BACKUPS,
        retention_days: int = DEFAULT_RETENTION_DAYS,
    ):
        """
        Initialize the backup manager.
        
        Args:
            backup_dir: Directory to store backups. Defaults to ~/.md2jira/backups/
            max_backups: Maximum number of backups to keep per epic.
            retention_days: Delete backups older than this many days.
        """
        self.backup_dir = backup_dir or self.DEFAULT_BACKUP_DIR
        self.max_backups = max_backups
        self.retention_days = retention_days
        self._ensure_dir()
    
    def _ensure_dir(self) -> None:
        """Ensure the backup directory exists."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_backup_id(self, epic_key: str) -> str:
        """Generate a unique backup ID."""
        # Include microseconds for uniqueness within same second
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        content = f"{epic_key}:{timestamp}"
        short_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
        # Use shorter timestamp format in ID (exclude microseconds for readability)
        short_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{epic_key}_{short_timestamp}_{short_hash}"
    
    def _backup_file(self, backup_id: str) -> Path:
        """Get the path to a backup file."""
        return self.backup_dir / f"{backup_id}.json"
    
    def _epic_dir(self, epic_key: str) -> Path:
        """Get the directory for a specific epic's backups."""
        # Sanitize epic key for filesystem
        safe_key = epic_key.replace("/", "_").replace("\\", "_")
        return self.backup_dir / safe_key
    
    def create_backup(
        self,
        tracker: "IssueTrackerPort",
        epic_key: str,
        markdown_path: str,
        metadata: Optional[dict] = None,
    ) -> Backup:
        """
        Create a backup of the current Jira state for an epic.
        
        Fetches all children of the epic and captures their current state
        before any modifications are made.
        
        Args:
            tracker: Issue tracker port to fetch current state.
            epic_key: The epic key to backup.
            markdown_path: Path to the markdown file (for reference).
            metadata: Optional additional metadata to store.
            
        Returns:
            The created Backup object.
        """
        logger.info(f"Creating backup for epic {epic_key}")
        
        backup_id = self._generate_backup_id(epic_key)
        backup = Backup(
            backup_id=backup_id,
            epic_key=epic_key,
            markdown_path=markdown_path,
            metadata=metadata or {},
        )
        
        # Fetch all children of the epic
        try:
            issues = tracker.get_epic_children(epic_key)
            logger.debug(f"Found {len(issues)} issues to backup")
            
            for issue_data in issues:
                # Get comment count
                try:
                    comments = tracker.get_issue_comments(issue_data.key)
                    comments_count = len(comments)
                except Exception as e:
                    logger.warning(f"Could not fetch comments for {issue_data.key}: {e}")
                    comments_count = 0
                
                # Create snapshot
                snapshot = IssueSnapshot.from_issue_data(issue_data, comments_count)
                backup.issues.append(snapshot)
                
        except Exception as e:
            logger.error(f"Failed to fetch issues for backup: {e}")
            raise
        
        # Save backup
        self.save_backup(backup)
        
        # Cleanup old backups
        self._cleanup_old_backups(epic_key)
        
        logger.info(f"Backup created: {backup_id} ({backup.issue_count} issues)")
        return backup
    
    def save_backup(self, backup: Backup) -> Path:
        """
        Save a backup to disk.
        
        Args:
            backup: The backup to save.
            
        Returns:
            Path to the saved backup file.
        """
        # Use epic-specific subdirectory for organization
        epic_dir = self._epic_dir(backup.epic_key)
        epic_dir.mkdir(parents=True, exist_ok=True)
        
        backup_file = epic_dir / f"{backup.backup_id}.json"
        
        with open(backup_file, "w") as f:
            json.dump(backup.to_dict(), f, indent=2, default=str)
        
        logger.debug(f"Saved backup to {backup_file}")
        return backup_file
    
    def load_backup(self, backup_id: str, epic_key: Optional[str] = None) -> Optional[Backup]:
        """
        Load a backup from disk.
        
        Args:
            backup_id: The backup ID to load.
            epic_key: Optional epic key to narrow search.
            
        Returns:
            The loaded Backup, or None if not found.
        """
        # Try direct path first
        if epic_key:
            backup_file = self._epic_dir(epic_key) / f"{backup_id}.json"
            if backup_file.exists():
                return self._load_backup_file(backup_file)
        
        # Search all epic directories
        for epic_dir in self.backup_dir.iterdir():
            if epic_dir.is_dir():
                backup_file = epic_dir / f"{backup_id}.json"
                if backup_file.exists():
                    return self._load_backup_file(backup_file)
        
        logger.warning(f"Backup not found: {backup_id}")
        return None
    
    def _load_backup_file(self, path: Path) -> Optional[Backup]:
        """Load a backup from a specific file."""
        try:
            with open(path) as f:
                data = json.load(f)
            return Backup.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to load backup {path}: {e}")
            return None
    
    def list_backups(self, epic_key: Optional[str] = None) -> list[dict]:
        """
        List all available backups.
        
        Args:
            epic_key: Optional filter by epic key.
            
        Returns:
            List of backup summaries (id, epic, created_at, issue_count).
        """
        backups = []
        
        search_dirs = []
        if epic_key:
            epic_dir = self._epic_dir(epic_key)
            if epic_dir.exists():
                search_dirs.append(epic_dir)
        else:
            search_dirs = [d for d in self.backup_dir.iterdir() if d.is_dir()]
        
        for epic_dir in search_dirs:
            for backup_file in epic_dir.glob("*.json"):
                try:
                    with open(backup_file) as f:
                        data = json.load(f)
                    
                    backups.append({
                        "backup_id": data.get("backup_id", backup_file.stem),
                        "epic_key": data.get("epic_key", epic_dir.name),
                        "created_at": data.get("created_at", ""),
                        "issue_count": len(data.get("issues", [])),
                        "path": str(backup_file),
                    })
                except (json.JSONDecodeError, KeyError):
                    continue
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda b: b.get("created_at", ""), reverse=True)
        return backups
    
    def get_latest_backup(self, epic_key: str) -> Optional[Backup]:
        """
        Get the most recent backup for an epic.
        
        Args:
            epic_key: The epic key.
            
        Returns:
            The most recent Backup, or None if no backups exist.
        """
        backups = self.list_backups(epic_key)
        if not backups:
            return None
        
        return self.load_backup(backups[0]["backup_id"], epic_key)
    
    def delete_backup(self, backup_id: str, epic_key: Optional[str] = None) -> bool:
        """
        Delete a specific backup.
        
        Args:
            backup_id: The backup ID to delete.
            epic_key: Optional epic key to narrow search.
            
        Returns:
            True if deleted, False if not found.
        """
        # Search for the backup
        search_dirs = []
        if epic_key:
            epic_dir = self._epic_dir(epic_key)
            if epic_dir.exists():
                search_dirs.append(epic_dir)
        else:
            search_dirs = [d for d in self.backup_dir.iterdir() if d.is_dir()]
        
        for epic_dir in search_dirs:
            backup_file = epic_dir / f"{backup_id}.json"
            if backup_file.exists():
                backup_file.unlink()
                logger.info(f"Deleted backup: {backup_id}")
                return True
        
        return False
    
    def _cleanup_old_backups(self, epic_key: str) -> int:
        """
        Clean up old backups for an epic based on retention policy.
        
        Args:
            epic_key: The epic key.
            
        Returns:
            Number of backups deleted.
        """
        backups = self.list_backups(epic_key)
        deleted = 0
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        
        for i, backup in enumerate(backups):
            should_delete = False
            
            # Delete if over max count (keep only max_backups most recent)
            if i >= self.max_backups:
                should_delete = True
                logger.debug(f"Deleting backup {backup['backup_id']} (over limit)")
            
            # Delete if over retention period
            elif backup.get("created_at"):
                try:
                    created = datetime.fromisoformat(backup["created_at"])
                    if created < cutoff:
                        should_delete = True
                        logger.debug(f"Deleting backup {backup['backup_id']} (expired)")
                except ValueError:
                    pass
            
            if should_delete:
                if self.delete_backup(backup["backup_id"], epic_key):
                    deleted += 1
        
        if deleted:
            logger.info(f"Cleaned up {deleted} old backups for {epic_key}")
        
        return deleted
    
    def cleanup_all(self) -> int:
        """
        Clean up old backups for all epics.
        
        Returns:
            Total number of backups deleted.
        """
        total_deleted = 0
        
        for epic_dir in self.backup_dir.iterdir():
            if epic_dir.is_dir():
                epic_key = epic_dir.name
                total_deleted += self._cleanup_old_backups(epic_key)
        
        return total_deleted


def create_pre_sync_backup(
    tracker: "IssueTrackerPort",
    epic_key: str,
    markdown_path: str,
    backup_dir: Optional[Path] = None,
) -> Backup:
    """
    Convenience function to create a backup before sync.
    
    Args:
        tracker: Issue tracker to fetch current state.
        epic_key: Epic key to backup.
        markdown_path: Path to markdown file.
        backup_dir: Optional custom backup directory.
        
    Returns:
        The created Backup.
    """
    manager = BackupManager(backup_dir=backup_dir)
    return manager.create_backup(
        tracker=tracker,
        epic_key=epic_key,
        markdown_path=markdown_path,
        metadata={
            "trigger": "pre_sync",
            "sync_mode": "auto",
        },
    )

