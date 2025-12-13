# Quick Start

Get up and running with md2jira in 5 minutes.

## Step 1: Set Up Credentials

Create a `.env` file in your project directory:

```bash
JIRA_URL=https://your-company.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=your-api-token
```

::: warning
Add `.env` to your `.gitignore` to avoid committing secrets!
:::

## Step 2: Create Your Epic Markdown

Create `EPIC.md` with your user stories:

```markdown
# 🚀 My Project Epic

> **Epic: Building awesome features**

---

## User Stories

---

### 🔧 US-001: Set Up Project Infrastructure

| Field | Value |
|-------|-------|
| **Story Points** | 3 |
| **Priority** | 🔴 Critical |
| **Status** | 📋 Planned |

#### Description

**As a** developer
**I want** project infrastructure set up
**So that** the team can start development

#### Acceptance Criteria

- [ ] Repository initialized
- [ ] CI/CD pipeline configured
- [ ] Development environment documented

#### Subtasks

| # | Subtask | Description | SP | Status |
|---|---------|-------------|:--:|--------|
| 1 | Create repo | Initialize Git repository | 1 | 📋 Planned |
| 2 | Add CI/CD | Set up GitHub Actions | 1 | 📋 Planned |
| 3 | Write docs | Document setup process | 1 | 📋 Planned |

---

### 🚀 US-002: User Authentication

| Field | Value |
|-------|-------|
| **Story Points** | 5 |
| **Priority** | 🟡 High |
| **Status** | 📋 Planned |

#### Description

**As a** user
**I want** to log in securely
**So that** my data is protected

#### Acceptance Criteria

- [ ] Login form with validation
- [ ] JWT token authentication
- [ ] Password reset flow

#### Subtasks

| # | Subtask | Description | SP | Status |
|---|---------|-------------|:--:|--------|
| 1 | Login UI | Create login form | 2 | 📋 Planned |
| 2 | Auth backend | Implement JWT auth | 2 | 📋 Planned |
| 3 | Password reset | Add reset flow | 1 | 📋 Planned |

---
```

## Step 3: Preview Changes

Run md2jira in dry-run mode (default) to see what would change:

```bash
md2jira --markdown EPIC.md --epic PROJ-123
```

You'll see a detailed preview:

```
╭──────────────────────────────────────────────╮
│  md2jira - Jira Sync Preview                 │
╰──────────────────────────────────────────────╯

Epic: PROJ-123
Stories found: 2
Mode: DRY RUN (no changes will be made)

┌─────────────────────────────────────────────┐
│ US-001: Set Up Project Infrastructure       │
├─────────────────────────────────────────────┤
│ ➕ Would create 3 subtasks                  │
│ 📝 Would update description                 │
│ ⏳ Would sync status: Planned               │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ US-002: User Authentication                 │
├─────────────────────────────────────────────┤
│ ➕ Would create 3 subtasks                  │
│ 📝 Would update description                 │
│ ⏳ Would sync status: Planned               │
└─────────────────────────────────────────────┘

Summary: 2 stories, 6 subtasks to create
```

## Step 4: Execute Sync

When you're happy with the preview, execute the sync:

```bash
md2jira --markdown EPIC.md --epic PROJ-123 --execute
```

You'll be asked for confirmation:

```
This will modify 2 stories and create 6 subtasks in Jira.
Proceed? [y/N]: y
```

## Step 5: Verify in Jira

Check your Jira epic to see the synced issues:

- ✅ Stories linked to the epic
- ✅ Descriptions updated with As a/I want/So that format
- ✅ Subtasks created under each story
- ✅ Story points and status set

## Common Commands

```bash
# Sync descriptions only
md2jira -m EPIC.md -e PROJ-123 -x --phase descriptions

# Sync subtasks only
md2jira -m EPIC.md -e PROJ-123 -x --phase subtasks

# Sync specific story
md2jira -m EPIC.md -e PROJ-123 -x --story US-001

# Skip confirmation prompts (for CI/CD)
md2jira -m EPIC.md -e PROJ-123 -x --no-confirm

# Verbose output
md2jira -m EPIC.md -e PROJ-123 -v

# Export results to JSON
md2jira -m EPIC.md -e PROJ-123 -x --export results.json
```

## Backup & Rollback

md2jira automatically creates backups before sync:

```bash
# List backups
md2jira --list-backups

# View diff from backup
md2jira --diff-latest --epic PROJ-123

# Rollback to previous state
md2jira --rollback --epic PROJ-123 --execute
```

## Next Steps

- [Markdown Schema](/guide/schema) - Complete format reference
- [Configuration](/guide/configuration) - Config file options
- [CLI Reference](/reference/cli) - All command options

