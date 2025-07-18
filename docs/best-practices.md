# Advanced Usage and Best Practices

This guide covers advanced usage patterns and best practices for production use of effect-log.

## Table of Contents

- [Production Configuration](#production-configuration)
- [Performance Optimization](#performance-optimization)
- [Error Handling](#error-handling)
- [Monitoring and Observability](#monitoring-and-observability)
- [Security Considerations](#security-considerations)
- [Testing Strategies](#testing-strategies)
- [Deployment Patterns](#deployment-patterns)
- [Advanced Patterns](#advanced-patterns)

## Production Configuration

### Environment-Based Configuration

```python
import os
from effect_log import Logger, LogLevel
from effect_log.writers import MultiWriter, JSONConsoleWriter, FileWriter, BufferedWriter

def create_production_logger():
    """Create production-ready logger configuration."""
    
    # Environment variables
    env = os.getenv("ENV", "development")
    log_level = LogLevel[os.getenv("LOG_LEVEL", "INFO")]
    service_name = os.getenv("SERVICE_NAME", "unknown")
    service_version = os.getenv("SERVICE_VERSION", "unknown")
    
    # Writers based on environment
    writers = []
    
    if env == "production":
        # JSON console output for production
        writers.append(JSONConsoleWriter(min_level=log_level))
        
        # Buffered file output for high throughput
        writers.append(BufferedWriter(
            FileWriter("/var/log/app/app.log", min_level=LogLevel.INFO),
            buffer_size=1000
        ))
        
        # Separate error log
        writers.append(FileWriter(
            "/var/log/app/errors.log",
            min_level=LogLevel.ERROR
        ))
    else:
        # Human-readable console output for development
        writers.append(ConsoleWriter(use_colors=True, min_level=log_level))
        
        # Optional file output for development
        if os.getenv("LOG_TO_FILE"):
            writers.append(FileWriter("dev.log"))
    
    # Create logger
    logger = Logger(
        writer=MultiWriter(*writers),
        min_level=log_level
    ).with_context(
        service=service_name,
        version=service_version,
        environment=env,
        hostname=os.getenv("HOSTNAME", "unknown"),
        instance_id=os.getenv("INSTANCE_ID", "unknown")
    )
    
    return logger

# Usage
logger = create_production_logger()
```

### Configuration Classes

```python
from dataclasses import dataclass
from typing import List, Optional
from effect_log import LogLevel

@dataclass
class LogConfig:
    """Configuration for logging setup."""
    
    service_name: str
    service_version: str
    environment: str
    log_level: LogLevel = LogLevel.INFO
    
    # Console settings
    console_enabled: bool = True
    console_json: bool = False
    console_colors: bool = True
    
    # File settings
    file_enabled: bool = False
    file_path: str = "app.log"
    file_buffer_size: int = 100
    
    # Error file settings
    error_file_enabled: bool = False
    error_file_path: str = "errors.log"
    
    # HTTP middleware settings
    http_log_requests: bool = True
    http_log_responses: bool = True
    http_include_headers: bool = False
    http_include_body: bool = False
    http_exclude_paths: List[str] = None
    
    def __post_init__(self):
        if self.http_exclude_paths is None:
            self.http_exclude_paths = ["/health", "/metrics", "/ready"]

def create_logger_from_config(config: LogConfig) -> Logger:
    """Create logger from configuration."""
    writers = []
    
    # Console writer
    if config.console_enabled:
        if config.console_json:
            writers.append(JSONConsoleWriter(min_level=config.log_level))
        else:
            writers.append(ConsoleWriter(
                use_colors=config.console_colors,
                min_level=config.log_level
            ))
    
    # File writer
    if config.file_enabled:
        file_writer = FileWriter(config.file_path, min_level=config.log_level)
        if config.file_buffer_size > 1:
            file_writer = BufferedWriter(file_writer, config.file_buffer_size)
        writers.append(file_writer)
    
    # Error file writer
    if config.error_file_enabled:
        writers.append(FileWriter(
            config.error_file_path,
            min_level=LogLevel.ERROR
        ))
    
    # Create logger
    logger = Logger(
        writer=MultiWriter(*writers) if len(writers) > 1 else writers[0],
        min_level=config.log_level
    ).with_context(
        service=config.service_name,
        version=config.service_version,
        environment=config.environment
    )
    
    return logger
```

## Performance Optimization

### Buffered Writing

```python
from effect_log.writers import BufferedWriter, FileWriter

# High-throughput logging
buffered_writer = BufferedWriter(
    FileWriter("high_volume.log"),
    buffer_size=5000  # Buffer 5000 entries
)

# Manual flush on shutdown
import atexit
atexit.register(buffered_writer.flush)
```

### Conditional Logging

```python
from effect_log.writers import FilterWriter

# Only log entries with specific conditions
performance_writer = FilterWriter(
    FileWriter("performance.log"),
    predicate=lambda entry: entry.context.get("duration_ms", 0) > 1000
)

# Error-only logging
error_writer = FilterWriter(
    FileWriter("errors.log"),
    predicate=lambda entry: entry.level >= LogLevel.ERROR
)
```

### Lazy Context Evaluation

```python
def expensive_context_calculation():
    """Expensive operation that should only run when logging."""
    # Some expensive computation
    return {"expensive_data": "result"}

# Use lambda for lazy evaluation
logger.info("Operation completed", 
    user_id="123",
    **expensive_context_calculation()  # Only evaluated if logging level allows
)
```

### Async Logging

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from effect_log.writers import Writer

class AsyncWriter:
    """Async wrapper for writers."""
    
    def __init__(self, writer: Writer, max_workers: int = 4):
        self.writer = writer
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def write(self, entry):
        """Write entry asynchronously."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor, self.writer.write, entry)
    
    def __del__(self):
        self.executor.shutdown(wait=True)

# Usage
async_writer = AsyncWriter(FileWriter("async.log"))
```

## Error Handling

### Structured Error Logging

```python
import traceback
from typing import Optional, Dict, Any

def log_exception(logger, exc: Exception, context: Optional[Dict[str, Any]] = None):
    """Log exception with full context."""
    error_context = {
        "error": str(exc),
        "error_type": type(exc).__name__,
        "error_module": type(exc).__module__,
        "traceback": traceback.format_exc(),
    }
    
    if context:
        error_context.update(context)
    
    logger.error("Exception occurred", **error_context)

# Usage
try:
    risky_operation()
except Exception as e:
    log_exception(logger, e, {
        "operation": "risky_operation",
        "user_id": "123",
        "input_data": input_data
    })
    raise
```

### Context Managers for Error Handling

```python
from contextlib import contextmanager

@contextmanager
def log_operation(logger, operation_name: str, **context):
    """Context manager for logging operations."""
    operation_logger = logger.with_context(operation=operation_name, **context)
    operation_logger.info("Operation started")
    
    start_time = time.time()
    try:
        yield operation_logger
        duration = time.time() - start_time
        operation_logger.info("Operation completed", duration_ms=duration * 1000)
    except Exception as e:
        duration = time.time() - start_time
        operation_logger.error("Operation failed",
            duration_ms=duration * 1000,
            error=str(e),
            error_type=type(e).__name__
        )
        raise

# Usage
with log_operation(logger, "user_registration", user_id="123") as op_logger:
    op_logger.debug("Validating user data")
    validate_user_data(user_data)
    
    op_logger.debug("Creating user in database")
    user = create_user(user_data)
    
    op_logger.info("User created successfully", user_id=user.id)
```

### Retry Logic with Logging

```python
import time
from typing import Callable, TypeVar, Optional

T = TypeVar('T')

def retry_with_logging(
    logger,
    func: Callable[[], T],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> T:
    """Retry function with exponential backoff and logging."""
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                wait_time = delay * (backoff ** (attempt - 1))
                logger.info("Retrying operation", 
                    attempt=attempt,
                    wait_time=wait_time,
                    max_retries=max_retries
                )
                time.sleep(wait_time)
            
            result = func()
            
            if attempt > 0:
                logger.info("Operation succeeded after retry", 
                    attempt=attempt,
                    total_attempts=attempt + 1
                )
            
            return result
            
        except exceptions as e:
            if attempt == max_retries:
                logger.error("Operation failed after all retries",
                    total_attempts=attempt + 1,
                    max_retries=max_retries,
                    error=str(e)
                )
                raise
            
            logger.warn("Operation failed, will retry",
                attempt=attempt + 1,
                error=str(e),
                remaining_retries=max_retries - attempt
            )

# Usage
result = retry_with_logging(
    logger.with_context(operation="fetch_user_data"),
    lambda: fetch_user_from_api(user_id),
    max_retries=3
)
```

## Monitoring and Observability

### Health Checks

```python
from datetime import datetime, timedelta
from typing import Dict, Any

class LoggingHealthCheck:
    """Health check for logging system."""
    
    def __init__(self, logger):
        self.logger = logger
        self.last_successful_log = datetime.now()
        self.error_count = 0
        self.max_errors = 10
    
    def check_health(self) -> Dict[str, Any]:
        """Check logging system health."""
        now = datetime.now()
        time_since_last_log = now - self.last_successful_log
        
        status = "healthy"
        issues = []
        
        # Check if logging is working
        try:
            self.logger.debug("Health check log entry")
            self.last_successful_log = now
        except Exception as e:
            self.error_count += 1
            issues.append(f"Logging error: {str(e)}")
            status = "unhealthy"
        
        # Check error rate
        if self.error_count > self.max_errors:
            issues.append(f"Too many logging errors: {self.error_count}")
            status = "unhealthy"
        
        # Check if logs are too old
        if time_since_last_log > timedelta(minutes=5):
            issues.append("No recent successful logs")
            status = "degraded"
        
        return {
            "status": status,
            "last_successful_log": self.last_successful_log.isoformat(),
            "error_count": self.error_count,
            "issues": issues
        }
```

### Metrics Collection

```python
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from threading import Lock

class LoggingMetrics:
    """Collect metrics about logging activity."""
    
    def __init__(self):
        self.lock = Lock()
        self.log_counts = Counter()
        self.error_counts = Counter()
        self.response_times = defaultdict(list)
        self.start_time = datetime.now()
    
    def record_log(self, level: LogLevel, duration_ms: float = None):
        """Record a log entry."""
        with self.lock:
            self.log_counts[level.name] += 1
            if duration_ms is not None:
                self.response_times[level.name].append(duration_ms)
    
    def record_error(self, error_type: str):
        """Record an error."""
        with self.lock:
            self.error_counts[error_type] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        with self.lock:
            uptime = datetime.now() - self.start_time
            
            # Calculate averages
            avg_response_times = {}
            for level, times in self.response_times.items():
                if times:
                    avg_response_times[level] = sum(times) / len(times)
            
            return {
                "uptime_seconds": uptime.total_seconds(),
                "log_counts": dict(self.log_counts),
                "error_counts": dict(self.error_counts),
                "average_response_times_ms": avg_response_times,
                "total_logs": sum(self.log_counts.values()),
                "total_errors": sum(self.error_counts.values())
            }

# Usage with custom writer
class MetricsWriter:
    """Writer that records metrics."""
    
    def __init__(self, writer: Writer, metrics: LoggingMetrics):
        self.writer = writer
        self.metrics = metrics
    
    def write(self, entry):
        start_time = time.time()
        try:
            self.writer.write(entry)
            duration = (time.time() - start_time) * 1000
            self.metrics.record_log(entry.level, duration)
        except Exception as e:
            self.metrics.record_error(type(e).__name__)
            raise

metrics = LoggingMetrics()
metrics_writer = MetricsWriter(FileWriter("app.log"), metrics)
logger = Logger(writer=metrics_writer)
```

### Distributed Tracing Integration

```python
import uuid
from typing import Optional, Dict, Any
from contextlib import contextmanager

class TracingContext:
    """Context for distributed tracing."""
    
    def __init__(self):
        self.trace_id: Optional[str] = None
        self.span_id: Optional[str] = None
        self.parent_span_id: Optional[str] = None
    
    def new_trace(self) -> str:
        """Start a new trace."""
        self.trace_id = str(uuid.uuid4())
        self.span_id = str(uuid.uuid4())
        self.parent_span_id = None
        return self.trace_id
    
    def new_span(self, parent_span_id: Optional[str] = None) -> str:
        """Start a new span."""
        self.parent_span_id = parent_span_id or self.span_id
        self.span_id = str(uuid.uuid4())
        return self.span_id

# Global tracing context
tracing_context = TracingContext()

@contextmanager
def traced_operation(logger, operation_name: str, **context):
    """Context manager for traced operations."""
    # Generate span ID
    span_id = tracing_context.new_span()
    
    # Create traced logger
    traced_logger = logger.with_span(
        span_id, 
        tracing_context.trace_id
    ).with_context(
        operation=operation_name,
        parent_span_id=tracing_context.parent_span_id,
        **context
    )
    
    traced_logger.info("Span started")
    start_time = time.time()
    
    try:
        yield traced_logger
        duration = time.time() - start_time
        traced_logger.info("Span completed", duration_ms=duration * 1000)
    except Exception as e:
        duration = time.time() - start_time
        traced_logger.error("Span failed",
            duration_ms=duration * 1000,
            error=str(e)
        )
        raise

# Usage
tracing_context.new_trace()

with traced_operation(logger, "user_registration", user_id="123") as span_logger:
    span_logger.info("Validating user data")
    
    with traced_operation(span_logger, "database_operation") as db_logger:
        db_logger.info("Creating user in database")
```

## Security Considerations

### Sensitive Data Filtering

```python
import re
from typing import Any, Dict

class SensitiveDataFilter:
    """Filter sensitive data from log entries."""
    
    def __init__(self):
        self.patterns = [
            (re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'), '[CARD_NUMBER]'),
            (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL]'),
            (re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'), '[PHONE]'),
            (re.compile(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'), '[SSN]'),
        ]
        
        self.sensitive_keys = {
            'password', 'passwd', 'pwd', 'secret', 'token', 'key', 'auth',
            'authorization', 'cookie', 'session', 'csrf', 'api_key'
        }
    
    def filter_value(self, value: Any) -> Any:
        """Filter sensitive data from a value."""
        if isinstance(value, str):
            filtered = value
            for pattern, replacement in self.patterns:
                filtered = pattern.sub(replacement, filtered)
            return filtered
        elif isinstance(value, dict):
            return self.filter_dict(value)
        elif isinstance(value, list):
            return [self.filter_value(item) for item in value]
        return value
    
    def filter_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter sensitive data from a dictionary."""
        filtered = {}
        for key, value in data.items():
            if key.lower() in self.sensitive_keys:
                filtered[key] = '[FILTERED]'
            else:
                filtered[key] = self.filter_value(value)
        return filtered

# Custom writer with filtering
class FilteredWriter:
    """Writer that filters sensitive data."""
    
    def __init__(self, writer: Writer):
        self.writer = writer
        self.filter = SensitiveDataFilter()
    
    def write(self, entry):
        # Filter context
        filtered_context = self.filter.filter_dict(entry.context)
        
        # Filter message
        filtered_message = self.filter.filter_value(entry.message)
        
        # Create new entry with filtered data
        filtered_entry = LogEntry(
            timestamp=entry.timestamp,
            level=entry.level,
            message=filtered_message,
            context=filtered_context,
            span_id=entry.span_id,
            trace_id=entry.trace_id
        )
        
        self.writer.write(filtered_entry)

# Usage
filtered_writer = FilteredWriter(FileWriter("app.log"))
logger = Logger(writer=filtered_writer)
```

### Access Control

```python
from typing import Set, Optional
from enum import Enum

class LogLevel(Enum):
    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4
    FATAL = 5

class AccessLevel(Enum):
    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    RESTRICTED = 3

class AccessControlledWriter:
    """Writer that enforces access control."""
    
    def __init__(self, writer: Writer, max_access_level: AccessLevel):
        self.writer = writer
        self.max_access_level = max_access_level
    
    def write(self, entry):
        # Check access level in context
        access_level = entry.context.get('access_level', AccessLevel.PUBLIC)
        
        if isinstance(access_level, str):
            access_level = AccessLevel[access_level.upper()]
        
        if access_level.value <= self.max_access_level.value:
            self.writer.write(entry)
        # Otherwise, silently drop the log entry

# Usage
controlled_writer = AccessControlledWriter(
    FileWriter("app.log"),
    AccessLevel.INTERNAL
)

logger = Logger(writer=controlled_writer)

# This will be logged (PUBLIC <= INTERNAL)
logger.info("User login", access_level=AccessLevel.PUBLIC)

# This will be dropped (RESTRICTED > INTERNAL)
logger.info("Admin action", access_level=AccessLevel.RESTRICTED)
```

## Testing Strategies

### Test Doubles

```python
from effect_log.types import LogEntry
from typing import List

class MockWriter:
    """Mock writer for testing."""
    
    def __init__(self):
        self.entries: List[LogEntry] = []
    
    def write(self, entry: LogEntry):
        self.entries.append(entry)
    
    def get_logs(self, level: LogLevel = None) -> List[LogEntry]:
        """Get logged entries, optionally filtered by level."""
        if level is None:
            return self.entries.copy()
        return [entry for entry in self.entries if entry.level == level]
    
    def get_messages(self, level: LogLevel = None) -> List[str]:
        """Get logged messages."""
        return [entry.message for entry in self.get_logs(level)]
    
    def clear(self):
        """Clear logged entries."""
        self.entries.clear()

# Test usage
def test_user_service():
    # Arrange
    mock_writer = MockWriter()
    logger = Logger(writer=mock_writer)
    service = UserService(logger)
    
    # Act
    service.create_user("test@example.com")
    
    # Assert
    logs = mock_writer.get_logs()
    assert len(logs) == 1
    assert logs[0].message == "User created"
    assert logs[0].context["email"] == "test@example.com"
```

### Test Fixtures

```python
import pytest
from effect_log import Logger
from effect_log.writers import ConsoleWriter
from io import StringIO

@pytest.fixture
def logger():
    """Create logger for testing."""
    stream = StringIO()
    writer = ConsoleWriter(stream=stream, use_colors=False)
    return Logger(writer=writer)

@pytest.fixture
def captured_logs():
    """Capture logs for testing."""
    mock_writer = MockWriter()
    logger = Logger(writer=mock_writer)
    yield logger, mock_writer
    mock_writer.clear()

# Usage
def test_error_handling(captured_logs):
    logger, mock_writer = captured_logs
    
    # Test error logging
    logger.error("Test error", error_code=500)
    
    error_logs = mock_writer.get_logs(LogLevel.ERROR)
    assert len(error_logs) == 1
    assert error_logs[0].context["error_code"] == 500
```

### Integration Testing

```python
import tempfile
import os
from pathlib import Path

def test_file_logging():
    """Test file logging integration."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = Path(temp_dir) / "test.log"
        
        # Create logger with file writer
        logger = Logger(writer=FileWriter(log_file))
        
        # Log some entries
        logger.info("Test message 1", key="value1")
        logger.error("Test message 2", key="value2")
        
        # Verify file contents
        assert log_file.exists()
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 2
        
        # Parse JSON logs
        import json
        log1 = json.loads(lines[0])
        log2 = json.loads(lines[1])
        
        assert log1["message"] == "Test message 1"
        assert log1["context"]["key"] == "value1"
        assert log2["level"] == "ERROR"
```

## Deployment Patterns

### Containerized Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app

# Create log directory
RUN mkdir -p /var/log/app && chown -R appuser:appuser /var/log/app

USER appuser

CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    environment:
      - ENV=production
      - LOG_LEVEL=INFO
      - SERVICE_NAME=my-app
      - SERVICE_VERSION=1.0.0
    volumes:
      - ./logs:/var/log/app
    depends_on:
      - logstash

  logstash:
    image: docker.elastic.co/logstash/logstash:7.15.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
      - ./logs:/var/log/app
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: app
        image: my-app:latest
        env:
        - name: ENV
          value: "production"
        - name: LOG_LEVEL
          value: "INFO"
        - name: SERVICE_NAME
          value: "my-app"
        - name: SERVICE_VERSION
          value: "1.0.0"
        - name: HOSTNAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        volumeMounts:
        - name: log-volume
          mountPath: /var/log/app
      volumes:
      - name: log-volume
        emptyDir: {}
```

### Log Aggregation

```python
# Structured logging for aggregation
logger = Logger(
    writer=JSONConsoleWriter(),
    min_level=LogLevel.INFO
).with_context(
    service="my-app",
    version="1.0.0",
    environment="production",
    pod_name=os.getenv("HOSTNAME"),
    node_name=os.getenv("NODE_NAME"),
    cluster="production-cluster"
)

# Add correlation IDs for tracing
def add_correlation_id(request):
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    return logger.with_context(correlation_id=correlation_id)
```

## Advanced Patterns

### Plugin System

```python
from abc import ABC, abstractmethod
from typing import List

class LogPlugin(ABC):
    """Abstract base class for log plugins."""
    
    @abstractmethod
    def process_entry(self, entry: LogEntry) -> LogEntry:
        """Process a log entry."""
        pass

class TimestampPlugin(LogPlugin):
    """Add additional timestamp information."""
    
    def process_entry(self, entry: LogEntry) -> LogEntry:
        new_context = entry.context.copy()
        new_context.update({
            "timestamp_unix": entry.timestamp.timestamp(),
            "timestamp_iso": entry.timestamp.isoformat()
        })
        
        return LogEntry(
            timestamp=entry.timestamp,
            level=entry.level,
            message=entry.message,
            context=new_context,
            span_id=entry.span_id,
            trace_id=entry.trace_id
        )

class PluginWriter:
    """Writer that applies plugins."""
    
    def __init__(self, writer: Writer, plugins: List[LogPlugin]):
        self.writer = writer
        self.plugins = plugins
    
    def write(self, entry: LogEntry):
        processed_entry = entry
        for plugin in self.plugins:
            processed_entry = plugin.process_entry(processed_entry)
        self.writer.write(processed_entry)

# Usage
plugin_writer = PluginWriter(
    FileWriter("app.log"),
    [TimestampPlugin()]
)
logger = Logger(writer=plugin_writer)
```

### Dynamic Configuration

```python
import json
import threading
from pathlib import Path
from typing import Dict, Any

class DynamicLogger:
    """Logger with dynamic configuration."""
    
    def __init__(self, config_file: str):
        self.config_file = Path(config_file)
        self.config = {}
        self.logger = None
        self.lock = threading.Lock()
        
        self._load_config()
        self._create_logger()
        
        # Watch for config changes
        self._start_config_watcher()
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration."""
        return {
            "log_level": "INFO",
            "console_enabled": True,
            "file_enabled": False,
            "file_path": "app.log"
        }
    
    def _create_logger(self):
        """Create logger from current configuration."""
        writers = []
        
        if self.config.get("console_enabled", True):
            writers.append(ConsoleWriter())
        
        if self.config.get("file_enabled", False):
            writers.append(FileWriter(self.config.get("file_path", "app.log")))
        
        log_level = LogLevel[self.config.get("log_level", "INFO")]
        
        with self.lock:
            self.logger = Logger(
                writer=MultiWriter(*writers) if len(writers) > 1 else writers[0],
                min_level=log_level
            )
    
    def _start_config_watcher(self):
        """Start watching config file for changes."""
        # Implementation would use file watching library
        pass
    
    def get_logger(self) -> Logger:
        """Get current logger instance."""
        with self.lock:
            return self.logger

# Usage
dynamic_logger = DynamicLogger("config.json")
logger = dynamic_logger.get_logger()
```

This comprehensive guide should help you implement production-ready logging with effect-log, covering all aspects from basic configuration to advanced patterns and security considerations.