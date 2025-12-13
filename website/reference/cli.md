# CLI Reference

Complete reference for all md2jira command-line options.

## Synopsis

```bash
md2jira [OPTIONS]
```

## Required Options

| Option | Short | Description |
|--------|-------|-------------|
| `--markdown PATH` | `-m` | Path to markdown file |
| `--epic KEY` | `-e` | Jira epic key (e.g., PROJ-123) |

## Common Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--execute` | `-x` | Execute changes (vs dry-run) | `false` |
| `--no-confirm` | | Skip confirmation prompts | `false` |
| `--verbose` | `-v` | Enable verbose output | `false` |
| `--quiet` | `-q` | Suppress non-essential output | `false` |
| `--help` | `-h` | Show help message | |
| `--version` | | Show version | |

## Sync Options

| Option | Description | Values |
|--------|-------------|--------|
| `--phase PHASE` | Run specific sync phase | `all`, `descriptions`, `subtasks`, `comments`, `statuses` |
| `--story ID` | Filter to specific story | Story ID (e.g., `US-001`) |

## Configuration Options

| Option | Description |
|--------|-------------|
| `--config PATH` | Path to config file |
| `--jira-url URL` | Override Jira URL |
| `--project KEY` | Override project key |

## Output Options

| Option | Description |
|--------|-------------|
| `--output FORMAT` | Output format: `text`, `json` |
| `--export PATH` | Export results to JSON file |
| `--no-color` | Disable colored output |
| `--log-file PATH` | Write logs to file |
| `--log-format FORMAT` | Log format: `text`, `json` |
| `--audit-trail PATH` | Export audit trail to JSON |

## Validation Options

| Option | Description |
|--------|-------------|
| `--validate` | Validate markdown only (no sync) |

## Interactive Mode

| Option | Description |
|--------|-------------|
| `--interactive` | `-i` | Step-by-step guided sync |
| `--resume` | Resume interrupted sync |

## Backup & Recovery

| Option | Description |
|--------|-------------|
| `--no-backup` | Disable automatic backup |
| `--list-backups` | List available backups |
| `--diff-backup ID` | Show diff from backup |
| `--diff-latest` | Show diff from latest backup |
| `--restore-backup ID` | Restore from backup |
| `--rollback` | Rollback last sync |

## Shell Completions

| Option | Description |
|--------|-------------|
| `--completions SHELL` | Output completion script | `bash`, `zsh`, `fish` |

## Examples

### Basic Sync

```bash
# Preview changes (dry-run)
md2jira --markdown EPIC.md --epic PROJ-123

# Execute sync
md2jira --markdown EPIC.md --epic PROJ-123 --execute

# Short form
md2jira -m EPIC.md -e PROJ-123 -x
```

### Sync Specific Phases

```bash
# Sync descriptions only
md2jira -m EPIC.md -e PROJ-123 -x --phase descriptions

# Sync subtasks only
md2jira -m EPIC.md -e PROJ-123 -x --phase subtasks

# Sync comments only
md2jira -m EPIC.md -e PROJ-123 -x --phase comments

# Sync status transitions only
md2jira -m EPIC.md -e PROJ-123 -x --phase statuses
```

### Filter by Story

```bash
# Sync specific story
md2jira -m EPIC.md -e PROJ-123 -x --story US-001

# Multiple stories (run multiple times)
md2jira -m EPIC.md -e PROJ-123 -x --story US-001
md2jira -m EPIC.md -e PROJ-123 -x --story US-002
```

### CI/CD Usage

```bash
# No prompts, JSON output
md2jira -m EPIC.md -e PROJ-123 -x --no-confirm --output json

# Export results for processing
md2jira -m EPIC.md -e PROJ-123 -x --no-confirm --export results.json

# Quiet mode (errors only)
md2jira -m EPIC.md -e PROJ-123 -x --no-confirm -q
```

### Logging & Debugging

```bash
# Verbose output
md2jira -m EPIC.md -e PROJ-123 -v

# Write logs to file
md2jira -m EPIC.md -e PROJ-123 -x --log-file sync.log

# JSON logs (for log aggregation)
md2jira -m EPIC.md -e PROJ-123 -x --log-format json

# Full audit trail
md2jira -m EPIC.md -e PROJ-123 -x --audit-trail audit.json
```

### Backup & Recovery

```bash
# List backups
md2jira --list-backups

# View diff from latest backup
md2jira --diff-latest --epic PROJ-123

# View diff from specific backup
md2jira --diff-backup backup_20250113_120000 --epic PROJ-123

# Restore from backup (dry-run)
md2jira --restore-backup backup_20250113_120000 --epic PROJ-123

# Restore from backup (execute)
md2jira --restore-backup backup_20250113_120000 --epic PROJ-123 --execute

# Rollback last sync
md2jira --rollback --epic PROJ-123 --execute
```

### Interactive Mode

```bash
# Guided sync with previews
md2jira -m EPIC.md -e PROJ-123 --interactive

# Resume interrupted sync
md2jira -m EPIC.md -e PROJ-123 --resume
```

### Validation

```bash
# Validate markdown format only
md2jira -m EPIC.md -e PROJ-123 --validate
```

### Configuration

```bash
# Use specific config file
md2jira -m EPIC.md -e PROJ-123 --config ~/.md2jira-prod.yaml

# Override Jira URL
md2jira -m EPIC.md -e PROJ-123 --jira-url https://other.atlassian.net

# Override project
md2jira -m EPIC.md -e PROJ-123 --project OTHER
```

## Exit Codes

See [Exit Codes Reference](/reference/exit-codes) for detailed exit code documentation.

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | File not found |
| 4 | Connection error |
| 5 | Authentication error |
| 6 | Validation error |
| 64 | Partial success |
| 80 | Cancelled by user |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `JIRA_URL` | Jira instance URL |
| `JIRA_EMAIL` | Jira account email |
| `JIRA_API_TOKEN` | Jira API token |
| `JIRA_PROJECT` | Default project key |
| `MD2JIRA_VERBOSE` | Enable verbose output |
| `MD2JIRA_NO_COLOR` | Disable colored output |

See [Environment Variables](/guide/environment) for complete documentation.

