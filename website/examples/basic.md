# Basic Usage Examples

Common usage patterns for spectra.

## Your First Sync

### 1. Set Up Credentials

Create a `.env` file:

```bash
JIRA_URL=https://your-company.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=your-api-token
```

### 2. Create Your Markdown

Create `EPIC.md`:

```markdown
# 🚀 My First Epic

> **Epic: Getting started with spectra**

---

## User Stories

---

### 🔧 US-001: Setup Development Environment

| Field | Value |
|-------|-------|
| **Story Points** | 3 |
| **Priority** | 🔴 Critical |
| **Status** | 📋 Planned |

#### Description

**As a** developer
**I want** the development environment configured
**So that** I can start building features

#### Subtasks

| # | Subtask | Description | SP | Status |
|---|---------|-------------|:--:|--------|
| 1 | Install dependencies | Run npm install | 1 | 📋 Planned |
| 2 | Configure linting | Set up ESLint | 1 | 📋 Planned |
| 3 | Set up testing | Configure Jest | 1 | 📋 Planned |

---
```

### 3. Preview Changes

```bash
spectra --markdown EPIC.md --epic PROJ-123
```

### 4. Execute Sync

```bash
spectra --markdown EPIC.md --epic PROJ-123 --execute
```

## Common Scenarios

### Sync Only Descriptions

When you only want to update story descriptions:

```bash
spectra -m EPIC.md -e PROJ-123 -x --phase descriptions
```

### Sync Only Subtasks

When you only want to create/update subtasks:

```bash
spectra -m EPIC.md -e PROJ-123 -x --phase subtasks
```

### Sync Specific Story

Focus on a single story:

```bash
spectra -m EPIC.md -e PROJ-123 -x --story US-001
```

### Verbose Output

See detailed information about each operation:

```bash
spectra -m EPIC.md -e PROJ-123 -v
```

### Export Results

Save sync results to JSON:

```bash
spectra -m EPIC.md -e PROJ-123 -x --export results.json
```

Output:

```json
{
  "epic_key": "PROJ-123",
  "timestamp": "2025-01-13T10:30:00Z",
  "dry_run": false,
  "results": {
    "stories_processed": 5,
    "descriptions_updated": 5,
    "subtasks_created": 12,
    "subtasks_updated": 3,
    "statuses_synced": 5,
    "errors": []
  }
}
```

## Validation

### Validate Before Sync

Check your markdown format without syncing:

```bash
spectra -m EPIC.md -e PROJ-123 --validate
```

Output for valid file:

```
✓ Markdown validation passed
  - 5 stories found
  - 12 subtasks defined
  - All required fields present
```

Output for invalid file:

```
✗ Markdown validation failed

Errors:
  Line 15: Story "US-002" missing metadata table
  Line 42: Invalid status emoji "⏳" - use ✅, 🔄, or 📋
  Line 67: Subtasks table missing "SP" column
```

## Backup & Recovery

### List Backups

```bash
spectra --list-backups
```

Output:

```
Available backups:
  1. backup_20250113_103000 (PROJ-123) - 2 hours ago
  2. backup_20250113_090000 (PROJ-123) - 5 hours ago
  3. backup_20250112_150000 (PROJ-456) - yesterday
```

### View Changes Since Last Backup

```bash
spectra --diff-latest --epic PROJ-123
```

Output:

```diff
Story: PROJ-124 (US-001: Setup Development Environment)
  Description:
-   **As a** developer
-   **I want** the environment ready
+   **As a** developer
+   **I want** the development environment configured
+   **So that** I can start building features

  Subtasks:
+   [NEW] PROJ-125: Install dependencies
+   [NEW] PROJ-126: Configure linting
```

### Rollback Last Sync

Preview rollback:

```bash
spectra --rollback --epic PROJ-123
```

Execute rollback:

```bash
spectra --rollback --epic PROJ-123 --execute
```

## Interactive Mode

For step-by-step guided sync:

```bash
spectra -m EPIC.md -e PROJ-123 --interactive
```

Interactive session:

```
╭──────────────────────────────────────────────╮
│  spectra Interactive Mode                    │
╰──────────────────────────────────────────────╯

Found 5 stories to sync with PROJ-123

Story 1/5: US-001 - Setup Development Environment

Preview changes:
  📝 Update description
  ➕ Create 3 subtasks
  ⏳ Sync status (Planned → Open)

Apply changes to US-001? [y/n/s(kip)/q(uit)]: y

✓ Updated description
✓ Created subtask PROJ-125
✓ Created subtask PROJ-126
✓ Created subtask PROJ-127
✓ Status synced

Story 2/5: US-002 - User Authentication
...
```

## Configuration File Usage

### With YAML Config

```yaml
# .spectra.yaml
jira:
  url: https://company.atlassian.net
  project: PROJ

sync:
  descriptions: true
  subtasks: true
  comments: false
  statuses: true

markdown: ./docs/EPIC.md
epic: PROJ-123
```

Run with defaults from config:

```bash
spectra
```

Or override specific values:

```bash
spectra --epic PROJ-456
```

### With pyproject.toml

```toml
# pyproject.toml
[tool.spectra]
epic = "PROJ-123"

[tool.spectra.jira]
url = "https://company.atlassian.net"
project = "PROJ"

[tool.spectra.sync]
verbose = true
```

