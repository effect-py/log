# API Reference

This document provides comprehensive API documentation for effect-log.

## Table of Contents

- [Core Classes](#core-classes)
  - [Logger](#logger)
  - [LogLevel](#loglevel)
  - [LogEntry](#logentry)
  - [LogContext](#logcontext)
- [Writers](#writers)
  - [ConsoleWriter](#consolewriter)
  - [JSONConsoleWriter](#jsonconsolewriter)
  - [FileWriter](#filewriter)
  - [MultiWriter](#multiwriter)
  - [FilterWriter](#filterwriter)
  - [BufferedWriter](#bufferedwriter)
- [Middleware](#middleware)
  - [HttpLoggerMiddleware](#httploggerinterware)
  - [Framework Middleware](#framework-middleware)
- [Functional Composition](#functional-composition)
  - [with_context](#with_context)
  - [with_span](#with_span)
  - [with_writer](#with_writer)
  - [with_min_level](#with_min_level)
  - [fork_logger](#fork_logger)
  - [merge_loggers](#merge_loggers)

## Core Classes

### Logger

The main logger class that provides immutable functional logging with composable effects.

#### Constructor

```python
Logger(
    writer: Writer = None,
    context: LogContext = None,
    min_level: LogLevel = LogLevel.INFO
)
```

**Parameters:**
- `writer` (Writer, optional): The writer to use for output. Defaults to `ConsoleWriter()`.
- `context` (LogContext, optional): Initial context for the logger. Defaults to empty context.
- `min_level` (LogLevel, optional): Minimum log level to output. Defaults to `LogLevel.INFO`.

**Example:**
```python
from effect_log import Logger, LogLevel
from effect_log.writers import JSONConsoleWriter

logger = Logger(
    writer=JSONConsoleWriter(),
    min_level=LogLevel.DEBUG
)
```

#### Methods

##### `log(level: LogLevel, message: str, **kwargs: Any) -> None`

Log a message at the specified level with additional context.

**Parameters:**
- `level` (LogLevel): The log level
- `message` (str): The log message
- `**kwargs`: Additional context data

**Example:**
```python
logger.log(LogLevel.INFO, "User login", user_id="123", ip="192.168.1.1")
```

##### `trace(message: str, **kwargs: Any) -> None`

Log a trace level message.

**Example:**
```python
logger.trace("Entering function", function="process_data", args=["arg1", "arg2"])
```

##### `debug(message: str, **kwargs: Any) -> None`

Log a debug level message.

**Example:**
```python
logger.debug("Database query", query="SELECT * FROM users", duration_ms=45)
```

##### `info(message: str, **kwargs: Any) -> None`

Log an info level message.

**Example:**
```python
logger.info("User registration", user_id="456", email="user@example.com")
```

##### `warn(message: str, **kwargs: Any) -> None`

Log a warning level message.

**Example:**
```python
logger.warn("API rate limit approaching", current_rate=95, limit=100)
```

##### `error(message: str, **kwargs: Any) -> None`

Log an error level message.

**Example:**
```python
logger.error("Database connection failed", error="Connection timeout", retry_count=3)
```

##### `fatal(message: str, **kwargs: Any) -> None`

Log a fatal level message.

**Example:**
```python
logger.fatal("System shutdown", reason="Out of memory", memory_usage="99%")
```

##### `with_context(**kwargs: Any) -> Logger`

Create a new logger with additional context.

**Parameters:**
- `**kwargs`: Context data to add

**Returns:**
- `Logger`: A new logger instance with additional context

**Example:**
```python
user_logger = logger.with_context(user_id="123", session_id="abc456")
user_logger.info("User action", action="profile_update")
```

##### `with_span(span_id: str, trace_id: Optional[str] = None) -> Logger`

Create a new logger with span information for distributed tracing.

**Parameters:**
- `span_id` (str): The span identifier
- `trace_id` (str, optional): The trace identifier

**Returns:**
- `Logger`: A new logger instance with span information

**Example:**
```python
traced_logger = logger.with_span("span-123", "trace-456")
traced_logger.info("Processing request")
```

##### `with_writer(writer: Writer) -> Logger`

Create a new logger with a different writer.

**Parameters:**
- `writer` (Writer): The new writer to use

**Returns:**
- `Logger`: A new logger instance with the specified writer

**Example:**
```python
from effect_log.writers import FileWriter

file_logger = logger.with_writer(FileWriter("app.log"))
file_logger.info("This goes to file")
```

##### `with_min_level(min_level: LogLevel) -> Logger`

Create a new logger with a different minimum log level.

**Parameters:**
- `min_level` (LogLevel): The new minimum log level

**Returns:**
- `Logger`: A new logger instance with the specified minimum level

**Example:**
```python
debug_logger = logger.with_min_level(LogLevel.DEBUG)
debug_logger.debug("This will now be logged")
```

##### `pipe(*operations: Callable[[Logger], Logger]) -> Logger`

Apply a sequence of operations to create a new logger using functional composition.

**Parameters:**
- `*operations`: Functions that take a Logger and return a Logger

**Returns:**
- `Logger`: A new logger instance with all operations applied

**Example:**
```python
from effect_log import with_context, with_span, with_min_level

composed_logger = logger.pipe(
    with_context(service="api", version="1.0"),
    with_span("request-123"),
    with_min_level(LogLevel.DEBUG)
)
```

### LogLevel

Enumeration of log levels in ascending order of severity.

#### Values

- `LogLevel.TRACE = 0`: Detailed diagnostic information
- `LogLevel.DEBUG = 1`: Debug information
- `LogLevel.INFO = 2`: General information
- `LogLevel.WARN = 3`: Warning messages
- `LogLevel.ERROR = 4`: Error messages
- `LogLevel.FATAL = 5`: Fatal error messages

#### Methods

##### `__str__() -> str`

Returns the string representation of the log level.

**Example:**
```python
level = LogLevel.INFO
print(str(level))  # "INFO"
```

#### Comparison

Log levels support comparison operations:

```python
LogLevel.DEBUG < LogLevel.INFO  # True
LogLevel.ERROR >= LogLevel.WARN  # True
```

### LogEntry

Immutable data class representing a log entry.

#### Attributes

- `timestamp` (datetime): When the log entry was created
- `level` (LogLevel): The log level
- `message` (str): The log message
- `context` (Dict[str, Any]): Additional context data
- `span_id` (Optional[str]): Span identifier for tracing
- `trace_id` (Optional[str]): Trace identifier for tracing

#### Methods

##### `to_json() -> str`

Convert the log entry to a JSON string.

**Returns:**
- `str`: JSON representation of the log entry

**Example:**
```python
entry = LogEntry(
    timestamp=datetime.now(),
    level=LogLevel.INFO,
    message="Test message",
    context={"user_id": "123"}
)
json_str = entry.to_json()
```

##### `to_dict() -> Dict[str, Any]`

Convert the log entry to a dictionary.

**Returns:**
- `Dict[str, Any]`: Dictionary representation of the log entry

### LogContext

Immutable data class for managing log context.

#### Attributes

- `data` (Dict[str, Any]): Context data
- `span_id` (Optional[str]): Span identifier
- `trace_id` (Optional[str]): Trace identifier

#### Methods

##### `with_data(**kwargs: Any) -> LogContext`

Create a new context with additional data.

**Parameters:**
- `**kwargs`: Additional context data

**Returns:**
- `LogContext`: A new context instance with additional data

##### `with_span(span_id: str, trace_id: Optional[str] = None) -> LogContext`

Create a new context with span information.

**Parameters:**
- `span_id` (str): The span identifier
- `trace_id` (str, optional): The trace identifier

**Returns:**
- `LogContext`: A new context instance with span information

##### `merge(other: LogContext) -> LogContext`

Merge two contexts, with the other context taking precedence.

**Parameters:**
- `other` (LogContext): The context to merge

**Returns:**
- `LogContext`: A new merged context

## Writers

### ConsoleWriter

Writer that outputs to console with optional color formatting.

#### Constructor

```python
ConsoleWriter(
    stream: TextIO = sys.stdout,
    use_colors: bool = True,
    min_level: LogLevel = LogLevel.INFO
)
```

**Parameters:**
- `stream` (TextIO, optional): Output stream. Defaults to `sys.stdout`.
- `use_colors` (bool, optional): Whether to use ANSI color codes. Defaults to `True`.
- `min_level` (LogLevel, optional): Minimum level to output. Defaults to `LogLevel.INFO`.

**Example:**
```python
from effect_log.writers import ConsoleWriter
import sys

writer = ConsoleWriter(
    stream=sys.stderr,
    use_colors=False,
    min_level=LogLevel.DEBUG
)
```

#### Methods

##### `write(entry: LogEntry) -> None`

Write a log entry to the console.

### JSONConsoleWriter

Writer that outputs JSON to console.

#### Constructor

```python
JSONConsoleWriter(
    stream: TextIO = sys.stdout,
    min_level: LogLevel = LogLevel.INFO
)
```

**Parameters:**
- `stream` (TextIO, optional): Output stream. Defaults to `sys.stdout`.
- `min_level` (LogLevel, optional): Minimum level to output. Defaults to `LogLevel.INFO`.

**Example:**
```python
from effect_log.writers import JSONConsoleWriter

writer = JSONConsoleWriter(min_level=LogLevel.DEBUG)
```

### FileWriter

Writer that outputs to a file.

#### Constructor

```python
FileWriter(
    file_path: str | Path,
    min_level: LogLevel = LogLevel.INFO,
    append: bool = True
)
```

**Parameters:**
- `file_path` (str | Path): Path to the log file
- `min_level` (LogLevel, optional): Minimum level to output. Defaults to `LogLevel.INFO`.
- `append` (bool, optional): Whether to append to existing file. Defaults to `True`.

**Example:**
```python
from effect_log.writers import FileWriter

writer = FileWriter(
    "logs/app.log",
    min_level=LogLevel.WARN,
    append=True
)
```

### MultiWriter

Writer that outputs to multiple writers.

#### Constructor

```python
MultiWriter(*writers: Writer)
```

**Parameters:**
- `*writers`: Variable number of writers

**Example:**
```python
from effect_log.writers import MultiWriter, ConsoleWriter, FileWriter

writer = MultiWriter(
    ConsoleWriter(),
    FileWriter("app.log"),
    FileWriter("errors.log", min_level=LogLevel.ERROR)
)
```

### FilterWriter

Writer that filters entries based on a predicate.

#### Constructor

```python
FilterWriter(writer: Writer, predicate: Callable[[LogEntry], bool])
```

**Parameters:**
- `writer` (Writer): The underlying writer
- `predicate` (Callable): Function that returns `True` for entries to write

**Example:**
```python
from effect_log.writers import FilterWriter, FileWriter

# Only log entries with user_id
user_writer = FilterWriter(
    FileWriter("user_logs.log"),
    predicate=lambda entry: "user_id" in entry.context
)
```

### BufferedWriter

Writer that buffers entries and flushes them periodically.

#### Constructor

```python
BufferedWriter(writer: Writer, buffer_size: int = 100)
```

**Parameters:**
- `writer` (Writer): The underlying writer
- `buffer_size` (int, optional): Number of entries to buffer. Defaults to 100.

**Example:**
```python
from effect_log.writers import BufferedWriter, FileWriter

writer = BufferedWriter(
    FileWriter("app.log"),
    buffer_size=500
)
```

#### Methods

##### `flush() -> None`

Flush all buffered entries.

## Middleware

### HttpLoggerMiddleware

Framework-agnostic HTTP request/response logging middleware.

#### Constructor

```python
HttpLoggerMiddleware(
    logger: Logger,
    log_requests: bool = True,
    log_responses: bool = True,
    include_headers: bool = False,
    include_body: bool = False,
    max_body_size: int = 1024,
    exclude_paths: Optional[List[str]] = None
)
```

**Parameters:**
- `logger` (Logger): The logger to use
- `log_requests` (bool, optional): Whether to log requests. Defaults to `True`.
- `log_responses` (bool, optional): Whether to log responses. Defaults to `True`.
- `include_headers` (bool, optional): Whether to include headers. Defaults to `False`.
- `include_body` (bool, optional): Whether to include body content. Defaults to `False`.
- `max_body_size` (int, optional): Maximum body size to log. Defaults to 1024.
- `exclude_paths` (List[str], optional): Paths to exclude from logging.

**Example:**
```python
from effect_log.middleware import HttpLoggerMiddleware

middleware = HttpLoggerMiddleware(
    logger,
    include_headers=True,
    exclude_paths=["/health", "/metrics"]
)
```

### Framework Middleware

#### FlaskMiddleware

Flask-specific middleware wrapper.

```python
from effect_log.middleware import FlaskMiddleware

flask_middleware = FlaskMiddleware(http_middleware)
app = flask_middleware(app)
```

#### FastAPIMiddleware

FastAPI-specific middleware wrapper.

```python
from effect_log.middleware import FastAPIMiddleware

middleware = FastAPIMiddleware(http_middleware)
app.add_middleware(middleware)
```

#### DjangoMiddleware

Django-specific middleware wrapper.

```python
# In settings.py
MIDDLEWARE = [
    'effect_log.middleware.DjangoMiddleware',
    # ... other middleware
]
```

## Functional Composition

### with_context

Create a function that adds context to a logger.

```python
def with_context(**kwargs: Any) -> Callable[[Logger], Logger]
```

**Parameters:**
- `**kwargs`: Context data to add

**Returns:**
- `Callable[[Logger], Logger]`: Function that adds context to a logger

**Example:**
```python
from effect_log import with_context

add_user_context = with_context(user_id="123", session_id="abc")
user_logger = logger.pipe(add_user_context)
```

### with_span

Create a function that adds span information to a logger.

```python
def with_span(span_id: str, trace_id: Optional[str] = None) -> Callable[[Logger], Logger]
```

**Parameters:**
- `span_id` (str): The span identifier
- `trace_id` (str, optional): The trace identifier

**Returns:**
- `Callable[[Logger], Logger]`: Function that adds span information to a logger

**Example:**
```python
from effect_log import with_span

add_span = with_span("request-123", "trace-456")
traced_logger = logger.pipe(add_span)
```

### with_writer

Create a function that sets the writer on a logger.

```python
def with_writer(writer: Writer) -> Callable[[Logger], Logger]
```

**Parameters:**
- `writer` (Writer): The writer to use

**Returns:**
- `Callable[[Logger], Logger]`: Function that sets the writer on a logger

**Example:**
```python
from effect_log import with_writer
from effect_log.writers import FileWriter

set_file_writer = with_writer(FileWriter("app.log"))
file_logger = logger.pipe(set_file_writer)
```

### with_min_level

Create a function that sets the minimum level on a logger.

```python
def with_min_level(min_level: LogLevel) -> Callable[[Logger], Logger]
```

**Parameters:**
- `min_level` (LogLevel): The minimum log level

**Returns:**
- `Callable[[Logger], Logger]`: Function that sets the minimum level on a logger

**Example:**
```python
from effect_log import with_min_level

set_debug_level = with_min_level(LogLevel.DEBUG)
debug_logger = logger.pipe(set_debug_level)
```

### fork_logger

Create a copy of the logger for independent use.

```python
def fork_logger(logger: Logger) -> Logger
```

**Parameters:**
- `logger` (Logger): The logger to fork

**Returns:**
- `Logger`: A new logger instance with the same configuration

**Example:**
```python
from effect_log import fork_logger

independent_logger = fork_logger(logger)
```

### merge_loggers

Merge two loggers, with the second logger taking precedence.

```python
def merge_loggers(logger1: Logger, logger2: Logger) -> Logger
```

**Parameters:**
- `logger1` (Logger): The first logger
- `logger2` (Logger): The second logger (takes precedence)

**Returns:**
- `Logger`: A new merged logger

**Example:**
```python
from effect_log import merge_loggers

base_logger = Logger().with_context(service="api")
user_logger = Logger().with_context(user_id="123")
merged = merge_loggers(base_logger, user_logger)
```