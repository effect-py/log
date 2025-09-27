"""Writers for effect-log functional structured logging."""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from typing import Protocol, TextIO

from .types import LogEntry, LogLevel


class Writer(Protocol):
    """Protocol for log writers."""

    def write(self, entry: LogEntry) -> None:
        """Write a log entry."""
        ...


class ConsoleWriter:
    """Writer that outputs to console with optional color formatting."""

    def __init__(
        self,
        stream: TextIO = sys.stdout,
        use_colors: bool = True,
        min_level: LogLevel = LogLevel.INFO,
    ):
        self.stream = stream
        self.use_colors = use_colors
        self.min_level = min_level

        # ANSI color codes
        self._colors = {
            LogLevel.TRACE: "\033[90m",  # dark gray
            LogLevel.DEBUG: "\033[36m",  # cyan
            LogLevel.INFO: "\033[32m",  # green
            LogLevel.WARN: "\033[33m",  # yellow
            LogLevel.ERROR: "\033[31m",  # red
            LogLevel.FATAL: "\033[35m",  # magenta
        }
        self._reset = "\033[0m"

    def write(self, entry: LogEntry) -> None:
        """Write log entry to console."""
        if entry.level < self.min_level:
            return

        output = self._format_entry(entry)
        print(output, file=self.stream)

    def _format_entry(self, entry: LogEntry) -> str:
        """Format log entry for console output."""
        timestamp = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        level_str = entry.level.name.ljust(5)

        if self.use_colors:
            color = self._colors.get(entry.level, "")
            level_str = f"{color}{level_str}{self._reset}"

        parts = [f"[{timestamp}]", f"[{level_str}]", entry.message]

        # Add context if present
        if entry.context:
            context_str = " ".join(f"{k}={v}" for k, v in entry.context.items())
            parts.append(f"({context_str})")

        # Add span/trace info if present
        if entry.span_id:
            parts.append(f"span={entry.span_id}")
        if entry.trace_id:
            parts.append(f"trace={entry.trace_id}")

        return " ".join(parts)


class JSONConsoleWriter:
    """Writer that outputs JSON to console."""

    def __init__(
        self, stream: TextIO = sys.stdout, min_level: LogLevel = LogLevel.INFO
    ):
        self.stream = stream
        self.min_level = min_level

    def write(self, entry: LogEntry) -> None:
        """Write log entry as JSON to console."""
        if entry.level < self.min_level:
            return

        print(entry.to_json(), file=self.stream)


class FileWriter:
    """Writer that outputs to a file."""

    def __init__(
        self,
        file_path: str | Path,
        min_level: LogLevel = LogLevel.INFO,
        append: bool = True,
    ):
        self.file_path = Path(file_path)
        self.min_level = min_level
        self.append = append

        # Ensure directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, entry: LogEntry) -> None:
        """Write log entry to file."""
        if entry.level < self.min_level:
            return

        mode = "a" if self.append else "w"
        with open(self.file_path, mode, encoding="utf-8") as f:
            f.write(entry.to_json() + "\n")


class MultiWriter:
    """Writer that outputs to multiple writers."""

    def __init__(self, *writers: Writer):
        self.writers = writers

    def write(self, entry: LogEntry) -> None:
        """Write log entry to all writers."""
        for writer in self.writers:
            writer.write(entry)


class FilterWriter:
    """Writer that filters entries based on a predicate."""

    def __init__(self, writer: Writer, predicate: Callable[[LogEntry], bool]):
        self.writer = writer
        self.predicate = predicate

    def write(self, entry: LogEntry) -> None:
        """Write log entry if predicate returns True."""
        if self.predicate(entry):
            self.writer.write(entry)


class BufferedWriter:
    """Writer that buffers entries and flushes them."""

    def __init__(self, writer: Writer, buffer_size: int = 100):
        self.writer = writer
        self.buffer_size = buffer_size
        self.buffer: list[LogEntry] = []

    def write(self, entry: LogEntry) -> None:
        """Add entry to buffer and flush if necessary."""
        self.buffer.append(entry)
        if len(self.buffer) >= self.buffer_size:
            self.flush()

    def flush(self) -> None:
        """Flush all buffered entries."""
        for entry in self.buffer:
            self.writer.write(entry)
        self.buffer.clear()

    def __del__(self) -> None:
        """Flush remaining entries on destruction."""
        if self.buffer:
            self.flush()
