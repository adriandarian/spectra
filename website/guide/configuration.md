# Configuration

md2jira supports multiple configuration sources with clear precedence rules.

## Configuration Precedence

Configuration is loaded in this order (highest priority first):

1. **CLI arguments** - Command line flags override all other sources
2. **Environment variables** - `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`
3. **`.env` file** - In current directory or package directory
4. **Config files** - `.md2jira.yaml`, `.md2jira.toml`, or `pyproject.toml`

## Config File Locations

md2jira searches for config files in this order:

1. Explicit path via `--config` flag
2. Current working directory
3. User home directory (`~`)

## Config File Formats

### YAML (Recommended)

Create `.md2jira.yaml` or `.md2jira.yml`:

```yaml
# Jira connection settings (required)
jira:
  url: https://your-company.atlassian.net
  email: your-email@company.com
  api_token: your-api-token
  project: PROJ  # Optional: default project key
  story_points_field: customfield_10014  # Optional: custom field ID

# Sync settings (optional)
sync:
  verbose: false
  execute: false  # Set to true for live mode (default: dry-run)
  no_confirm: false  # Set to true to skip confirmation prompts
  descriptions: true
  subtasks: true
  comments: true
  statuses: true

# Default paths (optional)
markdown: ./epics/my-epic.md
epic: PROJ-123
```

### TOML

Create `.md2jira.toml`:

```toml
# Default paths
markdown = "./epics/my-epic.md"
epic = "PROJ-123"

# Jira connection settings
[jira]
url = "https://your-company.atlassian.net"
email = "your-email@company.com"
api_token = "your-api-token"
project = "PROJ"
story_points_field = "customfield_10014"

# Sync settings
[sync]
verbose = false
execute = false
no_confirm = false
descriptions = true
subtasks = true
comments = true
statuses = true
```

### pyproject.toml

Add a `[tool.md2jira]` section to your project's `pyproject.toml`:

```toml
[tool.md2jira]
epic = "PROJ-123"

[tool.md2jira.jira]
url = "https://your-company.atlassian.net"
email = "your-email@company.com"
api_token = "your-api-token"
project = "PROJ"

[tool.md2jira.sync]
verbose = true
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `JIRA_URL` | Jira instance URL (e.g., `https://company.atlassian.net`) |
| `JIRA_EMAIL` | Jira account email |
| `JIRA_API_TOKEN` | Jira API token ([generate here](https://id.atlassian.com/manage-profile/security/api-tokens)) |
| `JIRA_PROJECT` | Default project key |
| `MD2JIRA_VERBOSE` | Enable verbose output (`true`/`false`) |

## .env File

Create a `.env` file in your project root:

```bash
# .env
JIRA_URL=https://your-company.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-api-token
JIRA_PROJECT=PROJ
```

::: warning Security
Add `.env` to your `.gitignore`!
:::

## CLI Override Examples

```bash
# Override Jira URL
md2jira --markdown epic.md --epic PROJ-123 --jira-url https://other.atlassian.net

# Specify config file
md2jira --markdown epic.md --epic PROJ-123 --config ~/configs/md2jira-prod.yaml

# Override project
md2jira --markdown epic.md --epic PROJ-123 --project OTHER
```

## Security Best Practices

::: tip Security Recommendations

1. **Never commit secrets** - Add `.env` and config files with tokens to `.gitignore`
2. **Use environment variables** - For CI/CD, use environment variables instead of files
3. **Rotate tokens regularly** - Regenerate API tokens periodically
4. **Limit token scope** - Use tokens with minimal required permissions

:::

### Example `.gitignore` entries

```gitignore
# md2jira config with secrets
.env
.md2jira.yaml
.md2jira.yml
.md2jira.toml
```

## Configuration Reference

### Jira Settings

| Setting | Type | Description |
|---------|------|-------------|
| `jira.url` | string | Jira instance URL |
| `jira.email` | string | Account email for authentication |
| `jira.api_token` | string | API token |
| `jira.project` | string | Default project key |
| `jira.story_points_field` | string | Custom field ID for story points |

### Sync Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `sync.verbose` | boolean | `false` | Enable verbose output |
| `sync.execute` | boolean | `false` | Execute changes (vs dry-run) |
| `sync.no_confirm` | boolean | `false` | Skip confirmation prompts |
| `sync.descriptions` | boolean | `true` | Sync story descriptions |
| `sync.subtasks` | boolean | `true` | Sync subtasks |
| `sync.comments` | boolean | `true` | Sync comments |
| `sync.statuses` | boolean | `true` | Sync status transitions |

