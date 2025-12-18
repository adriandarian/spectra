# AI Agent Instructions

This file provides instructions for AI coding assistants (Claude, Cursor, Copilot, etc.) working on the spectra codebase.

## Before Submitting Changes

**Always run these commands to ensure code quality:**

```bash
# Format code
ruff format src tests

# Lint and auto-fix
ruff check src tests --fix

# Type checking
mypy src/spectra

# Run tests
pytest
```

## Quick Validation

Run all checks in sequence:

```bash
ruff format src tests && ruff check src tests --fix && mypy src/spectra && pytest
```

## Command Reference

| Task | Command |
|------|---------|
| Format | `ruff format src tests` |
| Lint | `ruff check src tests` |
| Lint + Fix | `ruff check src tests --fix` |
| Type Check | `mypy src/spectra` |
| Test | `pytest` |
| Test + Coverage | `pytest --cov=spectra` |
| Test Specific | `pytest tests/adapters/test_markdown_parser.py -v` |
| Install Dev | `pip install -e ".[dev]"` |

## Code Standards

### Python
- Python 3.11+ with full type hints on all functions
- Use `dataclass` for entities, `Enum` for constrained values
- Use `Protocol` for interfaces (structural subtyping)
- Absolute imports only: `from spectra.core.domain.entities import UserStory`

### Architecture
- Core depends on abstractions, adapters implement them
- Don't bypass ports layer for external systems
- New features need tests in `tests/` mirroring `src/` structure

### Testing
- Use pytest fixtures
- Use `tmp_path` for file operations
- Use `textwrap.dedent()` for multiline test strings

## Common Issues

### Ruff Errors
```bash
# See all errors
ruff check src tests

# Auto-fix what's possible
ruff check src tests --fix
```

### Mypy Errors
```bash
# Check specific file
mypy src/spectra/path/to/file.py

# Ignore missing imports (if needed)
mypy src/spectra --ignore-missing-imports
```

### Test Failures
```bash
# Run specific test with output
pytest tests/path/to/test.py -v -s

# Run tests matching pattern
pytest -k "test_parse" -v
```

## File Structure

```
src/spectra/
├── core/           # Domain (entities, enums, ports)
├── adapters/       # Infrastructure (parsers, API clients)
├── application/    # Use cases
└── cli/            # Commands

tests/              # Mirrors src structure
```

## Key Files

- `src/spectra/core/domain/entities.py` - Epic, UserStory, Subtask
- `src/spectra/core/domain/enums.py` - Status, Priority parsing
- `src/spectra/adapters/parsers/markdown.py` - Main parser
- `src/spectra/cli/app.py` - CLI entry point

