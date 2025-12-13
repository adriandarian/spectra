---
layout: home

hero:
  name: md2jira
  text: Markdown to Jira, Simplified
  tagline: A production-grade CLI tool for synchronizing markdown documentation with Jira. Write your epic docs in markdown, sync to Jira automatically.
  image:
    src: /hero-illustration.svg
    alt: md2jira
  actions:
    - theme: brand
      text: Get Started →
      link: /guide/getting-started
    - theme: alt
      text: View on GitHub
      link: https://github.com/adriandarian/md2jira

features:
  - icon: 🚀
    title: Full Epic Sync
    details: Sync user stories, subtasks, descriptions, and comments from markdown to Jira in one command. Your documentation stays in sync.
  - icon: 📝
    title: Markdown-Native
    details: Write your epic documentation in familiar markdown format. No need to learn new syntax or use clunky web interfaces.
  - icon: 🔄
    title: Smart Matching
    details: Fuzzy title matching between markdown stories and Jira issues. Works with your existing issues without manual linking.
  - icon: 🛡️
    title: Safe by Default
    details: Dry-run mode, confirmations, and detailed previews before any changes. Backup and rollback capabilities built-in.
  - icon: ⚡
    title: Command Pattern
    details: Undo-capable operations with full audit trail. Every change is tracked and can be reversed if needed.
  - icon: 🔌
    title: Plugin System
    details: Extensible architecture for custom parsers, trackers, and formatters. Build adapters for GitHub Issues, Linear, and more.
  - icon: 📊
    title: Rich CLI Output
    details: Beautiful terminal UI with progress bars, colored output, and detailed reports. JSON output mode for CI/CD integration.
  - icon: 🐳
    title: Docker Ready
    details: Run in containers with Docker or Docker Compose. Perfect for CI/CD pipelines and automated workflows.
---

<style>
:root {
  --vp-home-hero-name-color: transparent;
  --vp-home-hero-name-background: linear-gradient(135deg, #0052cc 0%, #2684ff 50%, #36b37e 100%);
}

.dark {
  --vp-home-hero-name-background: linear-gradient(135deg, #2684ff 0%, #4c9aff 50%, #36b37e 100%);
}
</style>

## Quick Install

::: code-group

```bash [pip]
pip install md2jira
```

```bash [pipx]
pipx install md2jira
```

```bash [Homebrew]
brew install adriandarian/md2jira/md2jira
```

```bash [Docker]
docker pull adriandarian/md2jira:latest
```

:::

## Example Usage

```bash
# Preview changes (dry-run)
md2jira --markdown EPIC.md --epic PROJ-123

# Execute sync
md2jira --markdown EPIC.md --epic PROJ-123 --execute

# Sync with interactive mode
md2jira --markdown EPIC.md --epic PROJ-123 --execute --interactive
```

## What People Are Saying

> "md2jira transformed our sprint planning. We write everything in markdown and sync to Jira in seconds."

> "Finally, a tool that understands developers prefer markdown over clicking through Jira forms."

> "The backup and rollback features give us confidence to sync without fear."

