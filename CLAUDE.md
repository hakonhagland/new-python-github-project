# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a PyQt6 application that helps users create new Python GitHub projects with proper structure and configuration. The app provides a GUI for initializing Python projects with src/test directories, pyproject.toml, docs, .git, and .github directories.

## Architecture

The application follows a 3-area GUI layout:
- **A1 (Tasks)**: Top area showing a list of tasks, some requiring user input
- **A2 (Actions)**: Middle area with action buttons (e.g., "Create" button)
- **A3 (Terminal Output)**: Bottom area showing terminal-like log output

### Key Components
- `main.py`: CLI entry point with Click commands (`create`, `edit-config`)
- `main_window.py`: Main PyQt6 window implementing the 3-area layout
- `task.py`: Task management and task item widgets
- `config.py`: Configuration file handling
- `helpers.py`: Utility functions for app lifecycle
- `runtime.py`: Dependency checking

## Development Commands

### Virtual Environment
Always activate the virtual environment before running commands:
```bash
source .venv/bin/activate
```

### Common Commands
```bash
# Run tests
pytest tests/
make test

# Type checking
mypy --strict src/ tests/
make mypy

# Linting and formatting
ruff check src tests
ruff check --fix src tests
ruff format src tests
make ruff-check
make ruff-fix
make ruff-format

# Coverage (requires 100%)
coverage run -m pytest tests
coverage report -m
make coverage

# Build documentation
cd docs && make clean && make html
make docs
make view-docs  # Opens docs in browser

# Build and publish
uv build
make publish-to-pypi

# Run all tests across Python versions
tox
make tox

# Check RST documentation
make rstcheck

# Run pre-commit hooks manually
make pre-commit
```

### Docker Development
```bash
# Build Docker image
make docker-image

# Run in Docker container (with X11 forwarding)
make docker-container
```

## Git Workflow Requirements

**Important**: This project has specific git commit requirements from Cursor rules:
- Before changing/adding files: check for uncommitted changes
- If uncommitted files exist: run `git add .` and create a commit
- Exception: When fixing errors from previous response, ask user about committing
- **Always activate virtual environment before running git commands**

### Pre-commit Hooks

This project uses pre-commit hooks for code quality checks. **Critical**: You must activate the virtual environment before committing:

```bash
# Required workflow for commits
source .venv/bin/activate
git add .
git commit -m "your message"  # Hooks will now work properly
```

**Why virtual environment is required**: Pre-commit hooks inherit the shell environment. If the virtual environment isn't activated, hooks that depend on tools like `coverage` (installed in `.venv`) will fail with "command not found" errors.

**Alternative approaches**:
- Run hooks manually first: `make pre-commit` (after activating venv)
- Bypass failing hooks if needed: `git commit --no-verify -m "message"`

The project includes these pre-commit hooks:
- `trim-trailing-whitespace`: Remove trailing whitespace
- `end-of-file-fixer`: Ensure files end with newline
- `check-yaml`: Validate YAML syntax
- `ruff`: Python linting
- `ruff-format`: Python code formatting
- `mypy`: Type checking
- `rstcheck`: reStructuredText validation
- `coverage`: Test coverage verification

## Configuration

- Uses `platformdirs` for cross-platform config file locations
- Templates stored in `src/new_python_github_project/data/templates/`
- Default config in `src/new_python_github_project/data/default_config.ini`

## Testing

- Target: 100% test coverage (enforced in pyproject.toml)
- Uses pytest with pytest-qt for GUI testing
- pytest-xvfb for headless testing
- Tests located in `tests/` directory

## Code Style

Follow the Python style guide in `.cursor/rules/python.mdc`:
- 88 character line length (Black compatible)
- Use f-strings for string interpolation
- reStructuredText docstrings for all public APIs
- Type hints for all function parameters and return types
- Use `ruff` for formatting/linting and `mypy` for type checking
- Import order: standard library → third-party → local (alphabetically sorted)
- Functions/methods organized alphabetically within their scope

## Mypy

- Always verify that added coded has sufficient type annotations by running
 `make mypy` (`mypy --strict src/ tests/`)
