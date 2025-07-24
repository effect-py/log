"""Tests for Logger class."""

from datetime import datetime
from unittest.mock import Mock, patch

from effect_log import (
    Logger,
    LogLevel,
    with_context,
    with_min_level,
    with_span,
    with_writer,
)


class TestLogger:
    """Test suite for Logger class."""

    def test_logger_creation(self):
        """Test basic logger creation."""
        logger = Logger()
        assert logger.writer is not None
        assert logger.context is not None
        assert logger.min_level == LogLevel.INFO

    def test_logger_with_custom_writer(self):
        """Test logger with custom writer."""
        writer = Mock()
        logger = Logger(writer=writer)
        assert logger.writer is writer

    def test_logger_with_context(self):
        """Test adding context to logger."""
        logger = Logger()
        new_logger = logger.with_context(service="api", version="1.0")

        assert new_logger is not logger  # Should be immutable
        assert new_logger.context.data["service"] == "api"
        assert new_logger.context.data["version"] == "1.0"
        assert logger.context.data == {}  # Original unchanged

    def test_logger_with_span(self):
        """Test adding span information to logger."""
        logger = Logger()
        new_logger = logger.with_span("span-123", "trace-456")

        assert new_logger.context.span_id == "span-123"
        assert new_logger.context.trace_id == "trace-456"
        assert logger.context.span_id is None  # Original unchanged

    def test_logger_with_min_level(self):
        """Test setting minimum log level."""
        logger = Logger()
        new_logger = logger.with_min_level(LogLevel.DEBUG)

        assert new_logger.min_level == LogLevel.DEBUG
        assert logger.min_level == LogLevel.INFO  # Original unchanged

    def test_logger_pipe_operations(self):
        """Test functional composition with pipe."""
        writer = Mock()
        logger = Logger().pipe(
            with_writer(writer),
            with_context(service="api", version="1.0"),
            with_span("span-123"),
            with_min_level(LogLevel.DEBUG),
        )

        assert logger.writer is writer
        assert logger.context.data["service"] == "api"
        assert logger.context.span_id == "span-123"
        assert logger.min_level == LogLevel.DEBUG

    def test_log_methods(self):
        """Test various log level methods."""
        writer = Mock()
        logger = Logger(writer=writer)

        logger.trace("trace message")
        logger.debug("debug message")
        logger.info("info message")
        logger.warn("warn message")
        logger.error("error message")
        logger.fatal("fatal message")

        # Should only log INFO and above by default
        assert writer.write.call_count == 4

    def test_log_with_context(self):
        """Test logging with additional context."""
        writer = Mock()
        logger = Logger(writer=writer).with_context(service="api")

        logger.info("test message", user_id="123", action="create")

        writer.write.assert_called_once()
        entry = writer.write.call_args[0][0]
        assert entry.message == "test message"
        assert entry.context["service"] == "api"
        assert entry.context["user_id"] == "123"
        assert entry.context["action"] == "create"

    def test_log_level_filtering(self):
        """Test log level filtering."""
        writer = Mock()
        logger = Logger(writer=writer, min_level=LogLevel.WARN)

        logger.trace("trace")
        logger.debug("debug")
        logger.info("info")
        logger.warn("warn")
        logger.error("error")

        # Should only log WARN and above
        assert writer.write.call_count == 2

        calls = writer.write.call_args_list
        assert calls[0][0][0].level == LogLevel.WARN
        assert calls[1][0][0].level == LogLevel.ERROR

    def test_logger_immutability(self):
        """Test that loggers are immutable."""
        logger1 = Logger()
        logger2 = logger1.with_context(key="value")
        logger3 = logger2.with_span("span-123")

        # All should be different objects
        assert logger1 is not logger2
        assert logger2 is not logger3
        assert logger1 is not logger3

        # Original should be unchanged
        assert logger1.context.data == {}
        assert logger2.context.data == {"key": "value"}
        assert logger3.context.data == {"key": "value"}
        assert logger3.context.span_id == "span-123"

    @patch("effect_log.logger.datetime")
    def test_log_entry_creation(self, mock_datetime):
        """Test log entry creation with proper timestamp."""
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = mock_now

        writer = Mock()
        logger = Logger(writer=writer)

        logger.info("test message")

        writer.write.assert_called_once()
        entry = writer.write.call_args[0][0]
        assert entry.timestamp == mock_now
        assert entry.level == LogLevel.INFO
        assert entry.message == "test message"


class TestFunctionalComposition:
    """Test functional composition helpers."""

    def test_with_context_function(self):
        """Test with_context function."""
        logger = Logger()
        operation = with_context(service="api", version="1.0")
        new_logger = operation(logger)

        assert new_logger.context.data["service"] == "api"
        assert new_logger.context.data["version"] == "1.0"

    def test_with_span_function(self):
        """Test with_span function."""
        logger = Logger()
        operation = with_span("span-123", "trace-456")
        new_logger = operation(logger)

        assert new_logger.context.span_id == "span-123"
        assert new_logger.context.trace_id == "trace-456"

    def test_with_writer_function(self):
        """Test with_writer function."""
        writer = Mock()
        logger = Logger()
        operation = with_writer(writer)
        new_logger = operation(logger)

        assert new_logger.writer is writer

    def test_with_min_level_function(self):
        """Test with_min_level function."""
        logger = Logger()
        operation = with_min_level(LogLevel.DEBUG)
        new_logger = operation(logger)

        assert new_logger.min_level == LogLevel.DEBUG

    def test_chained_operations(self):
        """Test chaining multiple operations."""
        writer = Mock()
        logger = Logger()

        new_logger = logger.pipe(
            with_writer(writer),
            with_context(service="api"),
            with_span("span-123"),
            with_min_level(LogLevel.DEBUG),
        )

        assert new_logger.writer is writer
        assert new_logger.context.data["service"] == "api"
        assert new_logger.context.span_id == "span-123"
        assert new_logger.min_level == LogLevel.DEBUG
