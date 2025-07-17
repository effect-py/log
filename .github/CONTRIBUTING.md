# Contributing to effect-log

🎉 Thank you for your interest in contributing to effect-log! We welcome contributions from everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow:

- **Be respectful**: Treat everyone with respect and kindness
- **Be inclusive**: Welcome newcomers and help them learn
- **Be collaborative**: Work together to build something great
- **Be constructive**: Provide helpful feedback and suggestions

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- GitHub account

### Areas for Contribution

We welcome contributions in several areas:

- 🐛 **Bug fixes**: Help us squash bugs
- ✨ **New features**: Add new functionality
- 📚 **Documentation**: Improve docs and examples
- 🧪 **Tests**: Increase test coverage
- 🔧 **Performance**: Optimize performance
- 🎨 **Examples**: Create usage examples

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/log.git
cd log

# Add upstream remote
git remote add upstream https://github.com/effect-py/log.git
```

### 2. Set Up Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 3. Verify Setup

```bash
# Run tests to ensure everything works
pytest

# Run code quality checks
black --check .
ruff check .
mypy .
```

## Making Changes

### 1. Create a Branch

```bash
# Always create a new branch for your changes
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Branch Naming Convention

- **Features**: `feature/short-description`
- **Bug fixes**: `fix/short-description`
- **Documentation**: `docs/short-description`
- **Performance**: `perf/short-description`
- **Tests**: `test/short-description`

### 3. Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `style`: Code style changes (formatting, etc.)
- `chore`: Build process or auxiliary tool changes

**Examples:**
```
feat(logger): add support for custom log formatters

fix(writers): handle file permission errors gracefully

docs(readme): update installation instructions

test(logger): add tests for context composition
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=effect_log --cov-report=html

# Run specific test file
pytest tests/test_logger.py

# Run specific test
pytest tests/test_logger.py::test_basic_logging
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files as `test_*.py`
- Use descriptive test function names: `test_logger_with_context_creates_new_instance`
- Follow the Arrange-Act-Assert pattern:

```python
def test_logger_with_context_adds_context():
    # Arrange
    logger = Logger()
    
    # Act
    result = logger.with_context(user_id="123")
    
    # Assert
    assert result.default_context["user_id"] == "123"
    assert result is not logger  # Immutability check
```

### Test Coverage

- Aim for 90%+ test coverage
- Write tests for both happy paths and error cases
- Include edge cases and boundary conditions
- Test the public API, not internal implementation details

## Code Style

### Formatting

We use [Black](https://github.com/psf/black) for code formatting:

```bash
# Format all code
black .

# Check formatting
black --check .
```

### Linting

We use [Ruff](https://github.com/charliermarsh/ruff) for linting:

```bash
# Run linter
ruff check .

# Fix auto-fixable issues
ruff check . --fix
```

### Type Checking

We use [mypy](https://github.com/python/mypy) for type checking:

```bash
# Run type checker
mypy .
```

### Code Style Guidelines

- **Type hints**: All public functions must have type hints
- **Docstrings**: All public classes and functions must have docstrings
- **Immutability**: Prefer immutable data structures
- **Functional style**: Use functional programming patterns where appropriate
- **Error handling**: Use explicit error types and handle errors gracefully

### Docstring Style

Use Google-style docstrings:

```python
def log_message(level: LogLevel, message: str, context: Dict[str, Any]) -> None:
    """Log a message with the specified level and context.
    
    Args:
        level: The log level for the message
        message: The message to log
        context: Additional context data
        
    Raises:
        ValueError: If level is invalid
        
    Example:
        >>> logger = Logger()
        >>> logger.log_message(LogLevel.INFO, "Hello", {"user": "john"})
    """
```

## Submitting Changes

### 1. Before Submitting

```bash
# Ensure your branch is up to date
git fetch upstream
git rebase upstream/main

# Run all checks
pytest
black --check .
ruff check .
mypy .

# Run pre-commit to catch any issues
pre-commit run --all-files
```

### 2. Create Pull Request

1. Push your branch to your fork:
   ```bash
   git push origin your-branch-name
   ```

2. Create a pull request on GitHub
3. Fill out the pull request template
4. Link any related issues

### 3. Pull Request Guidelines

**Title:** Follow conventional commit format:
```
feat(logger): add support for custom formatters
```

**Description should include:**
- What changes were made
- Why the changes were necessary
- How to test the changes
- Any breaking changes
- Screenshots/examples if applicable

**Checklist:**
- [ ] Tests pass
- [ ] Code is formatted with Black
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG.md updated (for significant changes)

### 4. Review Process

- All PRs require at least one review
- Address reviewer feedback promptly
- Keep discussions constructive and focused
- Be patient - maintainers review PRs in their spare time

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### Pre-release Versions

For beta testing:
- `1.0.0b1` - Beta release
- `1.0.0rc1` - Release candidate

### Release Checklist

1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Create release PR
4. Tag release after merge
5. Publish to PyPI
6. Create GitHub release

## Getting Help

### Questions or Issues?

- 💬 **Discussions**: [GitHub Discussions](https://github.com/orgs/effect-py/discussions)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/effect-py/log/issues)
- 📧 **Email**: maintainers@effect-py.org

### Community

- Be patient with responses
- Search existing issues before creating new ones
- Provide clear, reproducible examples
- Be respectful and constructive

## Recognition

Contributors are recognized in several ways:

- **Contributors file**: Listed in CONTRIBUTORS.md
- **Release notes**: Mentioned in release announcements
- **GitHub**: Contributor badge on your profile

## Development Tips

### Useful Commands

```bash
# Watch tests during development
pytest-watch

# Run tests in parallel
pytest -n auto

# Generate coverage report
pytest --cov=effect_log --cov-report=html
open htmlcov/index.html

# Profile performance
python -m cProfile -o profile.stats examples/performance_test.py
```

### IDE Setup

**VS Code** - Recommended extensions:
- Python
- Black Formatter
- Ruff
- Python Type Hint
- Python Test Explorer

**PyCharm** - Enable:
- Black integration
- mypy integration
- pytest as test runner

### Local Testing

Test your changes with a real project:

```bash
# Install in development mode
pip install -e .

# In another project
pip install -e /path/to/effect-log

# Test your changes
from effect_log import Logger
logger = Logger()
logger.info("Testing my changes!")
```

Thank you for contributing to effect-log! 🚀
