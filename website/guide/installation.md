# Installation

md2jira can be installed using several methods. Choose the one that best fits your workflow.

## Prerequisites

- Python 3.10 or higher
- Jira Cloud account with API access

## Package Managers

### pip (Recommended)

```bash
pip install md2jira
```

### pipx (Isolated Environment)

[pipx](https://pipx.pypa.io/) installs Python CLI tools in isolated environments:

```bash
pipx install md2jira
```

### Homebrew (macOS/Linux)

```bash
brew install adriandarian/md2jira/md2jira
```

### Chocolatey (Windows)

```bash
choco install md2jira
```

### Universal Linux Installer

```bash
curl -fsSL https://raw.githubusercontent.com/adriandarian/md2jira/main/packaging/linux/install.sh | bash
```

## Docker

### Pull from Docker Hub

```bash
docker pull adriandarian/md2jira:latest
```

### Run with Docker

```bash
docker run --rm \
  -e JIRA_URL=https://your-company.atlassian.net \
  -e JIRA_EMAIL=your.email@company.com \
  -e JIRA_API_TOKEN=your-api-token \
  -v $(pwd):/workspace \
  md2jira:latest \
  --markdown EPIC.md --epic PROJ-123
```

### Docker Compose

For easier usage with persistent configuration:

```yaml
# docker-compose.yml
services:
  md2jira:
    image: adriandarian/md2jira:latest
    env_file:
      - .env
    volumes:
      - .:/workspace
    working_dir: /workspace
```

```bash
# Run with Docker Compose
docker compose run --rm md2jira --markdown EPIC.md --epic PROJ-123
```

## From Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/adriandarian/md2jira.git
cd md2jira
pip install -e ".[dev]"
```

This installs md2jira in editable mode with development dependencies (pytest, mypy, ruff, etc.).

## Verify Installation

Check that md2jira is installed correctly:

```bash
md2jira --version
```

Expected output:
```
md2jira version 1.0.0
```

## Shell Completions

Enable tab completion for your shell:

::: code-group

```bash [Bash]
eval "$(md2jira --completions bash)"
```

```bash [Zsh]
eval "$(md2jira --completions zsh)"
```

```fish [Fish]
md2jira --completions fish | source
```

:::

See [Shell Completions](/guide/completions) for permanent installation.

## Jira API Token

You'll need a Jira API token to authenticate. Generate one at:

[https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

::: tip Security Best Practice
Never commit your API token to version control. Use environment variables or a `.env` file (added to `.gitignore`).
:::

## Next Steps

- [Quick Start Guide](/guide/quick-start) - Your first sync in 5 minutes
- [Configuration](/guide/configuration) - Set up config files and environment variables

