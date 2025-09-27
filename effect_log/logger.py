"""Main Logger class for effect-log functional structured logging."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any, TypeVar

from .types import LogContext, LogEntry, LogLevel
from .writers import ConsoleWriter, Writer

T = TypeVar("T")


class Logger:
    """Immutable functional logger with composable effects."""

    def __init__(
        self,
        writer: Writer | None = None,
        context: LogContext | None = None,
        min_level: LogLevel = LogLevel.INFO,
    ):
        self.writer = writer or ConsoleWriter()
        self.context = context or LogContext()
        self.min_level = min_level

    def pipe(self, *operations: Callable[[Logger], Logger]) -> Logger:
        """Apply a sequence of operations to create a new logger."""
        result = self
        for operation in operations:
            result = operation(result)
        return result

    def with_writer(self, writer: Writer) -> Logger:
        """Create new logger with different writer."""
        return Logger(writer=writer, context=self.context, min_level=self.min_level)

    def with_context(self, **kwargs: Any) -> Logger:
        """Create new logger with additional context."""
        new_context = self.context.with_data(**kwargs)
        return Logger(writer=self.writer, context=new_context, min_level=self.min_level)

    def with_span(self, span_id: str, trace_id: str | None = None) -> Logger:
        """Create new logger with span information."""
        new_context = self.context.with_span(span_id, trace_id)
        return Logger(writer=self.writer, context=new_context, min_level=self.min_level)

    def with_min_level(self, min_level: LogLevel) -> Logger:
        """Create new logger with different minimum level."""
        return Logger(writer=self.writer, context=self.context, min_level=min_level)

    def log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        """Log a message at the specified level."""
        if level < self.min_level:
            return

        # Merge context with additional kwargs
        entry_context = {**self.context.data, **kwargs}

        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            message=message,
            context=entry_context,
            span_id=self.context.span_id,
            trace_id=self.context.trace_id,
        )

        self.writer.write(entry)

    def trace(self, message: str, **kwargs: Any) -> None:
        """Log a trace message."""
        self.log(LogLevel.TRACE, message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message."""
        self.log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message."""
        self.log(LogLevel.INFO, message, **kwargs)

    def warn(self, message: str, **kwargs: Any) -> None:
        """Log a warning message."""
        self.log(LogLevel.WARN, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message."""
        self.log(LogLevel.ERROR, message, **kwargs)

    def fatal(self, message: str, **kwargs: Any) -> None:
        """Log a fatal message."""
        self.log(LogLevel.FATAL, message, **kwargs)


# Functional composition helpers
def with_writer(writer: Writer) -> Callable[[Logger], Logger]:
    """Create a function that sets the writer on a logger."""

    def apply(logger: Logger) -> Logger:
        return logger.with_writer(writer)

    return apply


def with_context(**kwargs: Any) -> Callable[[Logger], Logger]:
    """Create a function that adds context to a logger."""

    def apply(logger: Logger) -> Logger:
        return logger.with_context(**kwargs)

    return apply


def with_span(span_id: str, trace_id: str | None = None) -> Callable[[Logger], Logger]:
    """Create a function that adds span information to a logger."""

    def apply(logger: Logger) -> Logger:
        return logger.with_span(span_id, trace_id)

    return apply


def with_min_level(min_level: LogLevel) -> Callable[[Logger], Logger]:
    """Create a function that sets the minimum level on a logger."""

    def apply(logger: Logger) -> Logger:
        return logger.with_min_level(min_level)

    return apply


def fork_logger(logger: Logger) -> Logger:
    """Create a copy of the logger for independent use."""
    return Logger(
        writer=logger.writer, context=logger.context, min_level=logger.min_level
    )


def merge_loggers(logger1: Logger, logger2: Logger) -> Logger:
    """Merge two loggers, with logger2 taking precedence."""
    merged_context = logger1.context.merge(logger2.context)
    return Logger(
        writer=logger2.writer, context=merged_context, min_level=logger2.min_level
    )
