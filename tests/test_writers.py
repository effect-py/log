"""Tests for writers module."""

import json
import tempfile
from datetime import datetime
from io import StringIO
from pathlib import Path
from unittest.mock import Mock

import pytest

from effect_log import LogEntry, LogLevel
from effect_log.writers import (
    BufferedWriter,
    ConsoleWriter,
    FileWriter,
    FilterWriter,
    JSONConsoleWriter,
    MultiWriter,
)


class TestConsoleWriter:
    """Test suite for ConsoleWriter."""
    
    def test_console_writer_basic(self):
        """Test basic console writer functionality."""
        stream = StringIO()
        writer = ConsoleWriter(stream=stream, use_colors=False)
        
        entry = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            level=LogLevel.INFO,
            message="test message",
            context={"key": "value"}
        )
        
        writer.write(entry)
        output = stream.getvalue()
        
        assert "2023-01-01 12:00:00" in output
        assert "INFO" in output
        assert "test message" in output
        assert "key=value" in output
    
    def test_console_writer_with_colors(self):
        """Test console writer with colors."""
        stream = StringIO()
        writer = ConsoleWriter(stream=stream, use_colors=True)
        
        entry = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            level=LogLevel.ERROR,
            message="error message"
        )
        
        writer.write(entry)
        output = stream.getvalue()
        
        assert "\033[31m" in output  # Red color for ERROR
        assert "\033[0m" in output   # Reset code
    
    def test_console_writer_level_filtering(self):
        """Test console writer level filtering."""
        stream = StringIO()
        writer = ConsoleWriter(stream=stream, min_level=LogLevel.WARN)
        
        debug_entry = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            level=LogLevel.DEBUG,
            message="debug message"
        )
        
        warn_entry = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            level=LogLevel.WARN,
            message="warn message"
        )
        
        writer.write(debug_entry)
        writer.write(warn_entry)
        
        output = stream.getvalue()
        assert "debug message" not in output
        assert "warn message" in output
    
    def test_console_writer_with_span(self):
        """Test console writer with span information."""
        stream = StringIO()
        writer = ConsoleWriter(stream=stream, use_colors=False)
        
        entry = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            level=LogLevel.INFO,
            message="test message",
            span_id="span-123",
            trace_id="trace-456"
        )
        
        writer.write(entry)
        output = stream.getvalue()
        
        assert "span=span-123" in output
        assert "trace=trace-456" in output


class TestJSONConsoleWriter:
    """Test suite for JSONConsoleWriter."""
    
    def test_json_console_writer_basic(self):
        """Test basic JSON console writer functionality."""
        stream = StringIO()
        writer = JSONConsoleWriter(stream=stream)
        
        entry = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            level=LogLevel.INFO,
            message="test message",
            context={"key": "value"}
        )
        
        writer.write(entry)
        output = stream.getvalue().strip()
        
        data = json.loads(output)
        assert data["timestamp"] == "2023-01-01T12:00:00"
        assert data["level"] == "INFO"
        assert data["message"] == "test message"
        assert data["context"]["key"] == "value"
    
    def test_json_console_writer_level_filtering(self):
        """Test JSON console writer level filtering."""
        stream = StringIO()
        writer = JSONConsoleWriter(stream=stream, min_level=LogLevel.ERROR)
        
        info_entry = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            level=LogLevel.INFO,
            message="info message"
        )
        
        error_entry = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            level=LogLevel.ERROR,
            message="error message"
        )
        
        writer.write(info_entry)
        writer.write(error_entry)
        
        output = stream.getvalue().strip()
        lines = output.split('\n')
        
        # Should only have one line (the error)
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["level"] == "ERROR"


class TestFileWriter:
    """Test suite for FileWriter."""
    
    def test_file_writer_basic(self):
        """Test basic file writer functionality."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_path = f.name
        
        try:
            writer = FileWriter(temp_path)
            
            entry = LogEntry(
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                level=LogLevel.INFO,
                message="test message",
                context={"key": "value"}
            )
            
            writer.write(entry)
            
            # Read the file and verify content
            with open(temp_path, 'r') as f:
                content = f.read().strip()
            
            data = json.loads(content)
            assert data["message"] == "test message"
            assert data["context"]["key"] == "value"
            
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_file_writer_append_mode(self):
        """Test file writer in append mode."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_path = f.name
        
        try:
            writer = FileWriter(temp_path, append=True)
            
            entry1 = LogEntry(
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                level=LogLevel.INFO,
                message="first message"
            )
            
            entry2 = LogEntry(
                timestamp=datetime(2023, 1, 1, 12, 0, 1),
                level=LogLevel.INFO,
                message="second message"
            )
            
            writer.write(entry1)
            writer.write(entry2)
            
            # Read the file and verify both entries
            with open(temp_path, 'r') as f:
                lines = f.read().strip().split('\n')
            
            assert len(lines) == 2
            data1 = json.loads(lines[0])
            data2 = json.loads(lines[1])
            assert data1["message"] == "first message"
            assert data2["message"] == "second message"
            
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_file_writer_directory_creation(self):
        """Test file writer creates directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "logs" / "app.log"
            writer = FileWriter(log_path)
            
            entry = LogEntry(
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                level=LogLevel.INFO,
                message="test message"
            )
            
            writer.write(entry)
            
            # Verify directory was created
            assert log_path.parent.exists()
            assert log_path.exists()


class TestMultiWriter:
    """Test suite for MultiWriter."""
    
    def test_multi_writer_basic(self):
        """Test basic multi writer functionality."""
        writer1 = Mock()
        writer2 = Mock()
        multi_writer = MultiWriter(writer1, writer2)
        
        entry = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            level=LogLevel.INFO,
            message="test message"
        )
        
        multi_writer.write(entry)
        
        writer1.write.assert_called_once_with(entry)
        writer2.write.assert_called_once_with(entry)
    
    def test_multi_writer_with_different_writers(self):
        """Test multi writer with different writer types."""
        stream1 = StringIO()
        stream2 = StringIO()
        
        writer1 = ConsoleWriter(stream=stream1, use_colors=False)
        writer2 = JSONConsoleWriter(stream=stream2)
        multi_writer = MultiWriter(writer1, writer2)
        
        entry = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            level=LogLevel.INFO,
            message="test message"
        )
        
        multi_writer.write(entry)
        
        output1 = stream1.getvalue()
        output2 = stream2.getvalue()
        
        # Console writer output
        assert "test message" in output1
        assert "INFO" in output1
        
        # JSON writer output
        data = json.loads(output2.strip())
        assert data["message"] == "test message"
        assert data["level"] == "INFO"


class TestFilterWriter:
    """Test suite for FilterWriter."""
    
    def test_filter_writer_basic(self):
        """Test basic filter writer functionality."""
        base_writer = Mock()
        
        # Filter to only allow ERROR level
        predicate = lambda entry: entry.level == LogLevel.ERROR
        filter_writer = FilterWriter(base_writer, predicate)
        
        info_entry = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            level=LogLevel.INFO,
            message="info message"
        )
        
        error_entry = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            level=LogLevel.ERROR,
            message="error message"
        )
        
        filter_writer.write(info_entry)
        filter_writer.write(error_entry)
        
        # Should only write the error entry
        base_writer.write.assert_called_once_with(error_entry)
    
    def test_filter_writer_context_filtering(self):
        """Test filter writer with context filtering."""
        base_writer = Mock()
        
        # Filter to only allow entries with service=api
        predicate = lambda entry: entry.context.get("service") == "api"
        filter_writer = FilterWriter(base_writer, predicate)
        
        api_entry = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            level=LogLevel.INFO,
            message="api message",
            context={"service": "api"}
        )
        
        web_entry = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            level=LogLevel.INFO,
            message="web message",
            context={"service": "web"}
        )
        
        filter_writer.write(api_entry)
        filter_writer.write(web_entry)
        
        # Should only write the api entry
        base_writer.write.assert_called_once_with(api_entry)


class TestBufferedWriter:
    """Test suite for BufferedWriter."""
    
    def test_buffered_writer_basic(self):
        """Test basic buffered writer functionality."""
        base_writer = Mock()
        buffered_writer = BufferedWriter(base_writer, buffer_size=2)
        
        entry1 = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            level=LogLevel.INFO,
            message="first message"
        )
        
        entry2 = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 1),
            level=LogLevel.INFO,
            message="second message"
        )
        
        # Write first entry - should not flush yet
        buffered_writer.write(entry1)
        base_writer.write.assert_not_called()
        
        # Write second entry - should flush both
        buffered_writer.write(entry2)
        assert base_writer.write.call_count == 2
        base_writer.write.assert_any_call(entry1)
        base_writer.write.assert_any_call(entry2)
    
    def test_buffered_writer_manual_flush(self):
        """Test manual flush of buffered writer."""
        base_writer = Mock()
        buffered_writer = BufferedWriter(base_writer, buffer_size=10)
        
        entry = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            level=LogLevel.INFO,
            message="test message"
        )
        
        buffered_writer.write(entry)
        base_writer.write.assert_not_called()
        
        buffered_writer.flush()
        base_writer.write.assert_called_once_with(entry)