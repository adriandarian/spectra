# spectra - Improvements Roadmap

This document tracks planned improvements, enhancements, and features for spectra before and after release.

---

## 🔴 Critical (Must Have Before Release)

These items are essential for a production-ready v1.0 release.

### Documentation & Community

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **CHANGELOG.md** | P0 | ✅ Done | Version history following [Keep a Changelog](https://keepachangelog.com/) format |
| **CONTRIBUTING.md** | P0 | ✅ Done | Contribution guidelines, PR process, code style |
| **CODE_OF_CONDUCT.md** | P0 | ✅ Done | Community standards (Contributor Covenant) |
| **SECURITY.md** | P0 | ✅ Done | Security policy, vulnerability reporting |
| **LICENSE verification** | P0 | ✅ Done | Ensure MIT license is complete and correct |

### Type Safety & Quality

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **py.typed marker** | P0 | ✅ Done | PEP 561 marker file for type hint support |
| **Type annotations audit** | P0 | ✅ Done | Ensure all public APIs have complete type hints |
| **Docstring coverage** | P0 | ✅ Done | All public classes/methods have docstrings |

### CI/CD & Automation

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **GitHub Actions - Tests** | P0 | ✅ Done | Run pytest on push/PR (Python 3.10, 3.11, 3.12) |
| **GitHub Actions - Lint** | P0 | ✅ Done | Run ruff, mypy, black checks |
| **GitHub Actions - Publish** | P0 | ❌ Todo | Auto-publish to PyPI on release tag |
| **Pre-commit hooks config** | P0 | ✅ Done | `.pre-commit-config.yaml` for local dev |
| **Dependabot config** | P1 | ✅ Done | Automated dependency updates |

### Testing

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **Integration tests** | P0 | ✅ Done | Tests with mocked Jira API responses |
| **CLI tests** | P0 | ✅ Done | Test argument parsing and output |
| **Fixtures file** | P1 | ✅ Done | Shared pytest fixtures in `conftest.py` |
| **Test coverage threshold** | P1 | ✅ Done | Enforce minimum coverage via `--cov-fail-under` in CI and `fail_under` in pyproject.toml (baseline: 70%, target: 80%+) |

### Configuration

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **Config file support** | P0 | ✅ Done | Support `.spectra.yaml`, `.spectra.toml`, and `pyproject.toml [tool.spectra]` |
| **Config validation** | P0 | ✅ Done | Clear, actionable error messages with config source guidance |
| **Config precedence docs** | P1 | ✅ Done | CLI > env > .env > config file (see `docs/CONFIG.md`) |

---

## 🟡 Recommended (Should Have)

These significantly improve user experience and maintainability.

### Error Handling & Resilience

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **Retry logic** | P1 | ✅ Done | Exponential backoff for transient failures |
| **Rate limiting** | P1 | ✅ Done | Respect Jira API rate limits, queue requests |
| **Connection pooling** | P2 | ✅ Done | Reuse HTTP connections for performance |
| **Timeout configuration** | P2 | ✅ Done | Configurable request timeouts |
| **Graceful degradation** | P2 | ✅ Done | Continue on partial failures, report at end |

### CLI Enhancements

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **Shell completions** | P1 | ✅ Done | Bash, Zsh, Fish autocomplete (`--completions`) |
| **Exit codes documentation** | P1 | ✅ Done | Documented in `docs/EXIT_CODES.md` with ExitCode enum |
| **Interactive mode** | P2 | ✅ Done | Step-by-step guided sync with previews (`--interactive`) |
| **Progress persistence** | P2 | ✅ Done | Resume interrupted syncs (`--resume`) |
| **Quiet mode** | P2 | ✅ Done | `--quiet/-q` flag for CI/scripting |
| **JSON output mode** | P2 | ✅ Done | `--output json` for programmatic use |

### Logging & Observability

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **Structured logging** | P1 | ✅ Done | `--log-format json` for log aggregation (ELK, Splunk, CloudWatch) |
| **Log levels** | P1 | ✅ Done | DEBUG/INFO via `--verbose` flag |
| **Log file output** | P2 | ✅ Done | `--log-file PATH` writes logs to file (in addition to stderr) |
| **Audit trail export** | P2 | ✅ Done | `--audit-trail PATH` exports all operations to structured JSON |

### Backup & Recovery

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **Backup before sync** | P1 | ✅ Done | Auto-backup Jira state before modifications (`--no-backup` to disable, `--list-backups` to view) |
| **Restore from backup** | P1 | ✅ Done | Restore Jira to previous state (`--restore-backup BACKUP_ID --execute`) |
| **Diff view** | P2 | ✅ Done | Show before/after diff for changes (`--diff-backup BACKUP_ID` or `--diff-latest --epic PROJ-123`) |
| **Rollback command** | P2 | ✅ Done | Undo last sync operation (`--rollback --epic PROJ-123 --execute`) |

### Deployment

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **Docker image** | P1 | ✅ Done | `Dockerfile` for containerized usage |
| **Docker Compose example** | P2 | ✅ Done | Example with environment setup |
| **Homebrew formula** | P2 | ✅ Done | `brew install spectra` support |
| **Chocolatey package** | P2 | ✅ Done | `choco install spectra` for Windows |
| **Linux packages** | P2 | ✅ Done | RPM spec, DEB control, universal installer script |

---

## 🟢 Nice to Have (Future Enhancements)

These add polish and expand functionality.

### Documentation Site

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **VitePress setup** | P2 | ✅ Done | Full documentation website with VitePress |
| **API reference** | P2 | ✅ Done | Core domain, ports, and hooks documentation |
| **Tutorial walkthroughs** | P3 | ✅ Done | Step-by-step guides with terminal demos for first sync, interactive mode, backup/restore, CI/CD |
| **Cookbook/recipes** | P3 | ✅ Done | Sprint planning, multi-team, migrations, bug triage, and more |

### Plugin Ecosystem

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **GitHub Issues adapter** | P2 | ✅ Done | Sync to GitHub Issues |
| **Linear adapter** | P2 | ✅ Done | Sync to Linear |
| **Azure DevOps adapter** | P2 | ✅ Done | Sync to Azure DevOps |
| **YAML parser plugin** | P2 | ✅ Done | Alternative to markdown input |
| **Notion parser plugin** | P3 | ✅ Done | Parse from Notion exports |
| **Confluence output** | P3 | ✅ Done | Sync to Confluence pages |

<!-- TODO: Come back later to rethink the project name - "spectra" is too narrow now that we support GitHub, Linear, Azure DevOps, Confluence, etc. Consider renaming to something more generic like "epic-sync", "story-sync", or "tracker-bridge" -->

### Advanced Features

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **Bidirectional sync** | P2 | ✅ Done | Sync changes FROM Jira back to markdown (`--pull`) |
| **Conflict detection** | P2 | ✅ Done | Detect and resolve sync conflicts (`--check-conflicts`, `--conflict-strategy`) |
| **Watch mode** | P2 | ✅ Done | Auto-sync on file changes (`--watch`) |
| **Scheduled sync** | P3 | ✅ Done | Cron-like scheduled syncs (`--schedule`) |
| **Webhook receiver** | P3 | ✅ Done | Receive Jira webhooks for reverse sync (`--webhook`) |
| **Multi-epic support** | P2 | ✅ Done | Sync multiple epics from one file (`--multi-epic`) |
| **Cross-project linking** | P3 | ✅ Done | Link stories across Jira projects (`--sync-links`) |

### Performance

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **Parallel API calls** | P2 | ✅ Done | Concurrent requests with asyncio (aiohttp, parallel execution utilities) |
| **Caching layer** | P2 | ✅ Done | Cache Jira responses to reduce API calls (MemoryCache, FileCache, TTL) |
| **Incremental sync** | P2 | ✅ Done | Only sync changed stories (content fingerprinting, ChangeTracker) |
| **Batch API operations** | P2 | ✅ Done | Use Jira bulk APIs (bulk create, parallel updates/transitions) |

### Developer Experience

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **VS Code extension** | P3 | ✅ Done | `vscode-extension/` with CodeLens and previews |
| **Neovim plugin** | P3 | ✅ Done | `nvim-plugin/` with Telescope integration |
| **GitHub Action** | P2 | ✅ Done | Ready-to-use action for CI pipelines (Docker-based, full options) |
| **Terraform provider** | P3 | ✅ Done | Infrastructure-as-code Jira management (Go-based, Plugin Framework) |

---

## 🔵 Technical Debt & Refactoring

Items to improve code quality and maintainability.

### Code Quality

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **Remove unused imports** | P1 | ✅ Done | Cleaned up 62 files (157 auto-fixed, 11 with noqa for optional deps) |
| **Consistent error handling** | P1 | ✅ Done | Created centralized `core/exceptions.py` with unified hierarchy |
| **Magic strings to constants** | P2 | ✅ Done | Created `core/constants.py` with HTTP, API, Jira field constants |
| **Reduce cyclomatic complexity** | P2 | ✅ Done | Refactored ADF formatter (CC:15→2) and orchestrator (CC:16→5) |

### Architecture

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **Async support** | P2 | ✅ Done | Added `AsyncIssueTrackerPort` and `AsyncJiraAdapter` for parallel ops |
| **Dependency injection container** | P2 | ✅ Done | Added `Container` with factories, lifecycles, testing utils |
| **Result type pattern** | P2 | ✅ Done | Added `Result[T,E]`, `Ok`, `Err` with combinators |
| **Specification pattern** | P3 | ✅ Done | Added composable `Specification` with and/or/not operators |

### Testing

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **Property-based testing** | P2 | ✅ Done | Added Hypothesis tests for Result, Spec, and domain objects |
| **Mutation testing** | P3 | ✅ Done | Added mutmut config, Makefile targets, and helper script |
| **Benchmark suite** | P3 | ✅ Done | Added pytest-benchmark with Result, Spec, Domain benchmarks |

---

## 📊 Metrics & Monitoring

For production deployments.

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **OpenTelemetry support** | P3 | ✅ Done | `--otel-enable` for tracing and metrics |
| **Prometheus metrics** | P3 | ✅ Done | `--prometheus` flag exports metrics for monitoring |
| **Health check endpoint** | P3 | ✅ Done | `--health` flag exposes /health, /live, /ready |
| **Usage analytics (opt-in)** | P3 | ✅ Done | `--analytics` for anonymous usage statistics |

---

## 🎨 UX Improvements

| Item | Priority | Status | Description |
|------|----------|--------|-------------|
| **Better error messages** | P1 | ✅ Done | Actionable error messages with suggestions |
| **Wizard for first-time setup** | P2 | ✅ Done | `spectra --init` command |
| **Template generator** | P2 | ✅ Done | `spectra --generate` from Jira epic |
| **Validation command** | P1 | ✅ Done | `spectra --validate` with comprehensive checks |
| **Status dashboard** | P3 | ✅ Done | `spectra --dashboard` TUI showing sync status |

---

## Priority Legend

| Priority | Meaning |
|----------|---------|
| **P0** | Blocker - must complete before release |
| **P1** | High - should complete before release |
| **P2** | Medium - nice for v1.0, okay for v1.1 |
| **P3** | Low - future enhancement |

## Status Legend

| Status | Meaning |
|--------|---------|
| ❌ Todo | Not started |
| 🔄 In Progress | Currently being worked on |
| ⚠️ Partial | Partially implemented |
| ✅ Done | Complete |

---

## Contributing

Want to help? Pick an item from this list and:

1. Open an issue to claim it
2. Fork the repo
3. Implement the feature
4. Submit a PR

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## Version Targets

### v1.0.0 (Initial Release)
- All P0 items complete
- Core sync functionality stable
- Basic documentation

### v1.1.0
- All P1 items complete
- Docker support
- Shell completions

### v2.0.0
- Plugin ecosystem
- Bidirectional sync
- Additional tracker adapters

---

*Last updated: December 2025*

