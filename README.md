# effect-log

🪵 **Functional structured logging with composable effects for Python**

[![PyPI version](https://badge.fury.io/py/effect-log.svg)](https://badge.fury.io/py/effect-log)
[![Python versions](https://img.shields.io/pypi/pyversions/effect-log.svg)](https://pypi.org/project/effect-log/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/effect-py/log/workflows/CI/badge.svg)](https://github.com/effect-py/log/actions)

Part of the [effect-py](https://github.com/effect-py) ecosystem - bringing functional programming patterns to Python.

## Features

- 🔄 **Composable Effects**: Chain logging operations with pipes
- 📊 **Structured Logging**: JSON output with rich context
- 🎯 **Type Safe**: Full type hints and mypy support
- 🔧 **Multiple Writers**: Console, file, buffered, and custom output targets
- 📈 **Observability**: Built-in tracing and span support
- 🧪 **Immutable**: Functional approach with immutable loggers
- 🌐 **HTTP Middleware**: Framework-agnostic HTTP request/response logging
- ⚡ **Performance**: Buffered writers and efficient processing
- 🔍 **Filtering**: Conditional logging with custom predicates

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
from effect_log import Logger, LogLevel
from effect_log.writers import JSONConsoleWriter, FileWriter, MultiWriter

# Production logger with JSON output
logger = Logger(
    writer=MultiWriter(
        JSONConsoleWriter(),
        FileWriter("app.log")
    ),
    min_level=LogLevel.INFO
).with_context(service="user-service")

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

### HTTP Middleware Integration

```python
from effect_log import Logger
from effect_log.middleware import HttpLoggerMiddleware

logger = Logger().with_context(service="web-api")
middleware = HttpLoggerMiddleware(logger, include_headers=True)

# Flask example
from flask import Flask
app = Flask(__name__)

@app.before_request
def log_request():
    from flask import request, g
    result = middleware(request)
    g.logger = result["logger"]
    g.request_id = result["request_id"]

@app.route("/users", methods=["POST"])
def create_user():
    from flask import g
    g.logger.info("Creating user", action="user_create")
    return {"status": "created"}
```

## API Reference

### Logger

The main `Logger` class provides immutable logging with functional composition.

#### Methods

- `trace(message, **context)` - Log trace level message
- `debug(message, **context)` - Log debug level message
- `info(message, **context)` - Log info level message
- `warn(message, **context)` - Log warning level message
- `error(message, **context)` - Log error level message
- `fatal(message, **context)` - Log fatal level message
- `with_context(**context)` - Create logger with additional context
- `with_span(span_id, trace_id=None)` - Create logger with tracing span
- `with_writer(writer)` - Create logger with different writer
- `with_min_level(level)` - Create logger with minimum log level
- `pipe(*operations)` - Apply operations in functional pipeline

### Writers

- `ConsoleWriter(use_colors=True, min_level=LogLevel.INFO)` - Write to console with optional colors
- `JSONConsoleWriter(min_level=LogLevel.INFO)` - Write JSON to console
- `FileWriter(file_path, min_level=LogLevel.INFO, append=True)` - Write to file
- `MultiWriter(*writers)` - Write to multiple destinations
- `FilterWriter(writer, predicate)` - Conditional writing
- `BufferedWriter(writer, buffer_size=100)` - Buffered writing for performance

### Functional Composition

- `with_context(**context)` - Curried context addition
- `with_span(span_id, trace_id=None)` - Curried span addition
- `with_writer(writer)` - Curried writer setting
- `with_min_level(level)` - Curried minimum level setting
- `fork_logger(logger)` - Create independent copy
- `merge_loggers(logger1, logger2)` - Merge two loggers

### Log Levels

Available log levels in ascending order of severity:
- `LogLevel.TRACE` - Detailed diagnostic information
- `LogLevel.DEBUG` - Debug information
- `LogLevel.INFO` - General information
- `LogLevel.WARN` - Warning messages
- `LogLevel.ERROR` - Error messages
- `LogLevel.FATAL` - Fatal error messages

### HTTP Middleware

The `HttpLoggerMiddleware` class provides framework-agnostic HTTP request/response logging:

```python
from effect_log.middleware import HttpLoggerMiddleware, FlaskMiddleware

# Generic middleware
middleware = HttpLoggerMiddleware(
    logger,
    include_headers=True,
    include_body=True,
    max_body_size=1024,
    exclude_paths=["/health", "/metrics"]
)

# Framework-specific helpers
flask_middleware = FlaskMiddleware(middleware)
```

### Performance Features

```python
from effect_log.writers import BufferedWriter, FilterWriter

# Buffered writing for high-throughput scenarios
buffered = BufferedWriter(FileWriter("app.log"), buffer_size=1000)

# Conditional logging to reduce overhead
error_only = FilterWriter(
    FileWriter("errors.log"),
    predicate=lambda entry: entry.level >= LogLevel.ERROR
)

logger = Logger(writer=MultiWriter(buffered, error_only))
```

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

## Framework Integration

### Flask Integration

```python
from flask import Flask, request, g
from effect_log import Logger
from effect_log.middleware import HttpLoggerMiddleware

app = Flask(__name__)
logger = Logger()
middleware = HttpLoggerMiddleware(logger)

@app.before_request
def before_request():
    result = middleware(request)
    g.logger = result["logger"]
    g.request_id = result["request_id"]

@app.route("/users")
def get_users():
    g.logger.info("Fetching users")
    return {"users": []}
```

### FastAPI Integration

```python
from fastapi import FastAPI, Request
from effect_log import Logger
from effect_log.middleware import FastAPIMiddleware

app = FastAPI()
logger = Logger()
middleware = FastAPIMiddleware(HttpLoggerMiddleware(logger))

app.add_middleware(middleware)

@app.get("/users")
async def get_users(request: Request):
    request.state.logger.info("Fetching users")
    return {"users": []}
```

### Django Integration

```python
# In settings.py
MIDDLEWARE = [
    'effect_log.middleware.DjangoMiddleware',
    # ... other middleware
]

# In views.py
def user_view(request):
    request.logger.info("User view accessed")
    return JsonResponse({"status": "success"})
```

## Best Practices

### 1. Use Structured Logging

Always include relevant context with your log messages:

```python
# Good
logger.info("User login", 
    user_id="123",
    ip_address="192.168.1.1",
    success=True,
    duration_ms=45
)

# Avoid
logger.info("User 123 logged in from 192.168.1.1 successfully in 45ms")
```

### 2. Create Specialized Loggers

Create loggers for different parts of your application:

```python
# Base logger for the service
base_logger = Logger().with_context(service="user-service", version="1.0.0")

# Specialized loggers
db_logger = base_logger.with_context(component="database")
cache_logger = base_logger.with_context(component="cache")
auth_logger = base_logger.with_context(component="auth")
```

### 3. Use Appropriate Log Levels

```python
# TRACE: Very detailed information
logger.trace("Entering function", function="calculate_score", args=args)

# DEBUG: Diagnostic information
logger.debug("Query executed", query=sql, duration_ms=23)

# INFO: General information
logger.info("User registered", user_id="123", email="user@example.com")

# WARN: Something unexpected happened
logger.warn("Rate limit approaching", current=95, limit=100)

# ERROR: Error occurred but application continues
logger.error("Payment failed", user_id="123", error="Card declined")

# FATAL: Critical error, application may stop
logger.fatal("Database unavailable", error="Connection refused")
```

### 4. Performance Considerations

```python
# Use buffered writers for high-volume logging
buffered_writer = BufferedWriter(FileWriter("app.log"), buffer_size=500)

# Use minimum log levels appropriately
production_logger = Logger(min_level=LogLevel.INFO)
debug_logger = Logger(min_level=LogLevel.DEBUG)

# Use filters for selective logging
error_writer = FilterWriter(
    FileWriter("errors.log"),
    predicate=lambda entry: entry.level >= LogLevel.ERROR
)
```

## Documentation

For comprehensive documentation, see the [docs](docs/) directory:

- [API Reference](docs/API.md) - Complete API documentation
- [Framework Integration](docs/integrations.md) - Detailed integration guides
- [Best Practices](docs/best-practices.md) - Production-ready recommendations
- [Migration Guide](docs/migration.md) - Migrating from other logging libraries
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions

## Contributing

Contributions are welcome! Please read our [Contributing Guide](.github/CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE) file.

## Related Projects

- [effect-py/http-client](https://github.com/effect-py/http-client) - Functional HTTP client
