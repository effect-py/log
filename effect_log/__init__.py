"""Effect-log: Functional structured logging with composable effects."""

from .logger import (
    Logger,
    fork_logger,
    merge_loggers,
    with_context,
    with_min_level,
    with_span,
    with_writer,
)
from .middleware import (
    DjangoMiddleware,
    FastAPIMiddleware,
    FlaskMiddleware,
    HttpLoggerMiddleware,
)
from .types import LogContext, LogEntry, LogLevel
from .writers import (
    BufferedWriter,
    ConsoleWriter,
    FileWriter,
    FilterWriter,
    JSONConsoleWriter,
    MultiWriter,
    Writer,
)

__version__ = "0.0.1"
__all__ = [
    # Core classes
    "Logger",
    "LogLevel",
    "LogEntry",
    "LogContext",
    # Writers
    "Writer",
    "ConsoleWriter",
    "JSONConsoleWriter",
    "FileWriter",
    "MultiWriter",
    "FilterWriter",
    "BufferedWriter",
    # Functional composition
    "with_context",
    "with_span",
    "with_writer",
    "with_min_level",
    "fork_logger",
    "merge_loggers",
    # Middleware
    "HttpLoggerMiddleware",
    "FlaskMiddleware",
    "FastAPIMiddleware",
    "DjangoMiddleware",
]
