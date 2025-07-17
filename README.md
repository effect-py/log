# effect-log

🪵 **Functional structured logging with composable effects for Python**

[![PyPI version](https://badge.fury.io/py/effect-log.svg)](https://badge.fury.io/py/effect-log)
[![Python versions](https://img.shields.io/pypi/pyversions/effect-log.svg)](https://pypi.org/project/effect-log/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/effect-py/log/workflows/Tests/badge.svg)](https://github.com/effect-py/log/actions)

Part of the [effect-py](https://github.com/effect-py) ecosystem - bringing functional programming patterns to Python.

## Features

- 🔄 **Composable Effects**: Chain logging operations with pipes
- 📊 **Structured Logging**: JSON output with rich context
- 🎯 **Type Safe**: Full type hints and mypy support
- 🔧 **Multiple Writers**: Console, file, and custom output targets
- 📈 **Observability**: Built-in tracing and span support
- 🧪 **Immutable**: Functional approach with immutable loggers
- ⚡ **Performance**: Lazy evaluation and efficient processing

## Installation

```bash
pip install effect-log
```

For development:
```bash
pip install effect-log[dev]
```

## Quick Start

```python
from effect_log import Logger, with_context, with_span

# Create logger
logger = Logger()

# Basic logging
logger.info("Application started", service="api", version="1.0.0")
logger.error("Database connection failed", error="timeout")

# Functional composition
request_logger = logger.pipe(
    with_context(request_id="req-123", user_id="user-456"),
    with_span("handle_request", "trace-789")
)

request_logger.info("Processing user request")
request_logger.warn("Rate limit approaching", current=95, limit=100)
```

## Advanced Usage

### Structured Production Logging

```python
from effect_log import Logger, ConsoleWriter, FileWriter, LogLevel

# Production logger with JSON output
logger = Logger(
    writers=[
        ConsoleWriter(format_json=True),
        FileWriter("app.log", format_json=True)
    ],
    min_level=LogLevel.INFO,
    service="user-service"
)

logger.info("Server started", port=8080, environment="production")
```

### Context Composition

```python
# Build context incrementally
base_logger = Logger().with_context(service="payment-api")
request_logger = base_logger.with_context(request_id="req-123")
user_logger = request_logger.with_context(user_id="user-456")

user_logger.info("Payment processed", amount=99.99, currency="USD")
# Output: {"level": "INFO", "message": "Payment processed", "context": {"service": "payment-api", "request_id": "req-123", "user_id": "user-456", "amount": 99.99, "currency": "USD"}}
```

### Integration with HTTP Clients

```python
from effect_log import Logger, HttpLoggerMiddleware

logger = Logger()
http_logger = HttpLoggerMiddleware(logger)

# Automatic HTTP request/response logging
http_logger.log_request("POST", "/users", user_data={"name": "John"})
http_logger.log_response("POST", "/users", 201, 45.2, user_id="123")
```

## API Reference

### Logger

The main `Logger` class provides immutable logging with functional composition.

#### Methods

- `info(message, **context)` - Log info level message
- `error(message, **context)` - Log error level message  
- `debug(message, **context)` - Log debug level message
- `warn(message, **context)` - Log warning level message
- `with_context(**context)` - Create logger with additional context
- `with_span(span_id, trace_id=None)` - Create logger with tracing span
- `pipe(*operations)` - Apply operations in functional pipeline

### Writers

- `ConsoleWriter(format_json=False)` - Write to stdout/stderr
- `FileWriter(filename, format_json=True)` - Write to file

### Functional Composition

- `with_context(**context)` - Curried context addition
- `with_span(span_id, trace_id=None)` - Curried span addition
- `log_info(message, **context)` - Curried info logging
- `log_error(message, **context)` - Curried error logging

## Development

### Setup

```bash
git clone https://github.com/effect-py/log.git
cd log
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Testing

```bash
pytest
```

### Code Quality

```bash
black .
ruff check .
mypy .
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE) file.

## Related Projects

- [effect-py/http-client](https://github.com/effect-py/http-client) - Functional HTTP client
