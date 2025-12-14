# spectra Configuration

spectra supports multiple configuration sources with the following precedence (highest first):

1. **CLI arguments** - Command line flags override all other sources
2. **Environment variables** - `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`
3. **`.env` file** - In current directory or package directory
4. **Config files** - `.spectra.yaml`, `.spectra.toml`, or `pyproject.toml`

## Config File Locations

spectra searches for config files in this order:

1. Explicit path via `--config` flag
2. Current working directory
3. User home directory (`~`)

## Config File Formats

### YAML (`.spectra.yaml` or `.spectra.yml`)

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

### TOML (`.spectra.toml`)

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

Add a `[tool.spectra]` section to your project's `pyproject.toml`:

```toml
[tool.spectra]
epic = "PROJ-123"

[tool.spectra.jira]
url = "https://your-company.atlassian.net"
email = "your-email@company.com"
api_token = "your-api-token"
project = "PROJ"

[tool.spectra.sync]
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

## Security Best Practices

1. **Never commit secrets** - Add `.env` and config files with tokens to `.gitignore`
2. **Use environment variables** - For CI/CD, use environment variables instead of files
3. **Rotate tokens regularly** - Regenerate API tokens periodically
4. **Limit token scope** - Use tokens with minimal required permissions

## Example `.gitignore` entries

```gitignore
# spectra config with secrets
.env
.spectra.yaml
.spectra.yml
.spectra.toml
```

## CLI Override Examples

```bash
# Override Jira URL
spectra --markdown epic.md --epic PROJ-123 --jira-url https://other.atlassian.net

# Specify config file
spectra --markdown epic.md --epic PROJ-123 --config ~/configs/spectra-prod.yaml

# Override project
spectra --markdown epic.md --epic PROJ-123 --project OTHER
```

