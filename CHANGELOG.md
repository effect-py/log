# Changelog
## [0.0.1] - 2025-09-30

### Added
- Release version 0.0.1

## [0.1.7] - 2025-09-30

### Added
- Release version 0.1.7

## [0.1.6] - 2025-09-30

### Added
- Release version 0.1.6

## [0.1.5] - 2025-09-30

### Added
- Release version 0.1.5

## [0.1.4] - 2025-09-29

### Added
- Release version 0.1.4

## [0.1.3] - 2025-09-29

### Added
- Release version 0.1.3

## [0.1.2] - 2025-09-29

### Added
- Release version 0.1.2

## [0.1.1] - 2025-09-29

### Added
- Release version 0.1.1

## [0.1.0] - 2025-09-27

### Added
- Release version 0.1.0


All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation suite
- Complete API reference
- Framework integration guides
- Best practices and advanced usage guide
- Migration guide from other logging libraries
- Troubleshooting guide

### Changed
- Improved project structure
- Enhanced GitHub Actions workflows
- Consolidated contributing documentation

## [0.1.0b1] - 2025-01-18

### Added
- Initial release of effect-log
- Core `Logger` class with functional composition
- Immutable logging with `with_context()` and `with_span()` methods
- Pipe operations for functional composition
- Multiple writers: `ConsoleWriter`, `JSONConsoleWriter`, `FileWriter`
- Advanced writers: `MultiWriter`, `FilterWriter`, `BufferedWriter`
- HTTP middleware for request/response logging
- Framework integration: Flask, FastAPI, Django support
- Distributed tracing support with span and trace IDs
- Structured logging with JSON output
- Six log levels: TRACE, DEBUG, INFO, WARN, ERROR, FATAL
- Type-safe implementation with full type hints
- Zero runtime dependencies
- Python 3.8+ support

### Features
- **Functional Composition**: Chain operations with `pipe()` method
- **Immutable Loggers**: All operations return new logger instances
- **Structured Context**: Rich context data with every log entry
- **Performance Optimized**: Buffered writing and efficient processing
- **Framework Agnostic**: Works with any Python web framework
- **Production Ready**: Comprehensive error handling and monitoring
- **Extensible**: Plugin architecture for custom writers and middleware

### Documentation
- Complete API reference
- User guide with examples
- Framework integration tutorials
- Best practices guide
- Migration documentation
- Troubleshooting guide

### Testing
- Comprehensive test suite
- 90%+ test coverage
- Framework integration tests
- Performance benchmarks
- Example validation

### Development
- Modern Python packaging with `pyproject.toml`
- GitHub Actions CI/CD pipeline
- Code quality tools: Black, Ruff, mypy
- Security scanning and vulnerability checks
- Automated dependency updates with Dependabot
- Comprehensive issue and PR templates

[Unreleased]: https://github.com/effect-py/log/compare/v0.1.0b1...HEAD
[0.1.0b1]: https://github.com/effect-py/log/releases/tag/v0.1.0b1