"""Core types for effect-log functional structured logging."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class LogLevel(Enum):
    """Log levels in ascending order of severity."""

    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4
    FATAL = 5

    def __str__(self) -> str:
        return self.name

    def __lt__(self, other: LogLevel) -> bool:
        return self.value < other.value

    def __le__(self, other: LogLevel) -> bool:
        return self.value <= other.value

    def __gt__(self, other: LogLevel) -> bool:
        return self.value > other.value

    def __ge__(self, other: LogLevel) -> bool:
        return self.value >= other.value


@dataclass(frozen=True)
class LogEntry:
    """Immutable log entry with structured data."""

    timestamp: datetime
    level: LogLevel
    message: str
    context: dict[str, Any] = field(default_factory=dict)
    span_id: str | None = None
    trace_id: str | None = None

    def to_json(self) -> str:
        """Convert log entry to JSON string."""
        data = {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.name,
            "message": self.message,
            "context": self.context,
        }

        if self.span_id:
            data["span_id"] = self.span_id
        if self.trace_id:
            data["trace_id"] = self.trace_id

        return json.dumps(data, separators=(",", ":"))

    def to_dict(self) -> dict[str, Any]:
        """Convert log entry to dictionary."""
        data = {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.name,
            "message": self.message,
            "context": self.context,
        }

        if self.span_id:
            data["span_id"] = self.span_id
        if self.trace_id:
            data["trace_id"] = self.trace_id

        return data


@dataclass(frozen=True)
class LogContext:
    """Immutable context for log entries."""

    data: dict[str, Any] = field(default_factory=dict)
    span_id: str | None = None
    trace_id: str | None = None

    def with_data(self, **kwargs: Any) -> LogContext:
        """Create new context with additional data."""
        new_data = {**self.data, **kwargs}
        return LogContext(data=new_data, span_id=self.span_id, trace_id=self.trace_id)

    def with_span(self, span_id: str, trace_id: str | None = None) -> LogContext:
        """Create new context with span information."""
        return LogContext(
            data=self.data, span_id=span_id, trace_id=trace_id or self.trace_id
        )

    def merge(self, other: LogContext) -> LogContext:
        """Merge two contexts, with other taking precedence."""
        merged_data = {**self.data, **other.data}
        return LogContext(
            data=merged_data,
            span_id=other.span_id or self.span_id,
            trace_id=other.trace_id or self.trace_id,
        )
