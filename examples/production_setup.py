"""Production setup examples for effect-log."""

import os
from datetime import datetime
from pathlib import Path

from effect_log import Logger, LogLevel
from effect_log.writers import (
    BufferedWriter,
    ConsoleWriter,
    FileWriter,
    FilterWriter,
    JSONConsoleWriter,
    MultiWriter,
)


def production_logger_setup():
    """Production-ready logger configuration."""
    print("=== Production Logger Setup ===")
    
    # Environment-based configuration
    env = os.getenv("ENV", "development")
    log_level = LogLevel[os.getenv("LOG_LEVEL", "INFO")]
    
    # Create log directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Console writer (structured JSON for production)
    if env == "production":
        console_writer = JSONConsoleWriter(min_level=log_level)
    else:
        console_writer = ConsoleWriter(use_colors=True, min_level=log_level)
    
    # File writers for different log types
    app_log_writer = FileWriter(
        log_dir / "app.log",
        min_level=LogLevel.INFO
    )
    
    error_log_writer = FileWriter(
        log_dir / "error.log",
        min_level=LogLevel.ERROR
    )
    
    # Buffered writer for performance
    buffered_app_writer = BufferedWriter(app_log_writer, buffer_size=100)
    
    # Multi-writer for comprehensive logging
    multi_writer = MultiWriter(
        console_writer,
        buffered_app_writer,
        error_log_writer
    )
    
    # Create production logger
    logger = Logger(
        writer=multi_writer,
        min_level=log_level
    ).with_context(
        service=os.getenv("SERVICE_NAME", "unknown"),
        version=os.getenv("SERVICE_VERSION", "unknown"),
        environment=env,
        instance_id=os.getenv("INSTANCE_ID", "unknown")
    )
    
    return logger


def microservice_logger():
    """Microservice-specific logger configuration."""
    print("\n=== Microservice Logger ===")
    
    # Base logger for the service
    base_logger = production_logger_setup()
    
    # Service-specific context
    service_logger = base_logger.with_context(
        service="user-service",
        version="2.1.0",
        deployment="k8s-cluster-1"
    )
    
    # Different loggers for different components
    components = {
        "database": service_logger.with_context(component="database"),
        "cache": service_logger.with_context(component="redis"),
        "queue": service_logger.with_context(component="rabbitmq"),
        "external_api": service_logger.with_context(component="external_api"),
    }
    
    # Example usage
    components["database"].info("Database connection established")
    components["cache"].info("Cache warmed up", keys_loaded=1500)
    components["queue"].info("Queue consumer started", queue_name="user_events")
    components["external_api"].warn("External API slow response", duration_ms=2500)
    
    return service_logger


def request_tracing_setup():
    """Request tracing and correlation setup."""
    print("\n=== Request Tracing Setup ===")
    
    import uuid
    
    base_logger = production_logger_setup()
    
    # Simulate request processing with tracing
    def process_request(user_id: str, operation: str):
        # Generate trace and span IDs
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        
        # Create request logger with tracing
        request_logger = base_logger.pipe(
            lambda l: l.with_context(
                user_id=user_id,
                operation=operation,
                request_id=f"req-{uuid.uuid4().hex[:8]}"
            ),
            lambda l: l.with_span(span_id, trace_id)
        )
        
        request_logger.info("Request started")
        
        # Simulate nested operations with child spans
        database_span = str(uuid.uuid4())
        db_logger = request_logger.with_span(database_span, trace_id)
        db_logger.info("Database query started", query="SELECT * FROM users")
        db_logger.info("Database query completed", rows_returned=1)
        
        cache_span = str(uuid.uuid4())
        cache_logger = request_logger.with_span(cache_span, trace_id)
        cache_logger.info("Cache lookup", key=f"user:{user_id}")
        cache_logger.info("Cache hit", key=f"user:{user_id}")
        
        request_logger.info("Request completed", status="success")
    
    # Process some requests
    process_request("user-123", "get_profile")
    process_request("user-456", "update_profile")


def error_handling_setup():
    """Error handling and alerting setup."""
    print("\n=== Error Handling Setup ===")
    
    # Create specialized error logger
    error_log_writer = FileWriter("logs/errors.log", min_level=LogLevel.ERROR)
    
    # Alert writer for critical errors
    class AlertWriter:
        def __init__(self, min_level=LogLevel.ERROR):
            self.min_level = min_level
        
        def write(self, entry):
            if entry.level >= self.min_level:
                # In production, this would send to alerting system
                print(f"=¨ ALERT: {entry.level.name} - {entry.message}")
                if entry.context:
                    print(f"   Context: {entry.context}")
    
    alert_writer = AlertWriter(min_level=LogLevel.ERROR)
    
    # Multi-writer for errors
    error_multi_writer = MultiWriter(
        ConsoleWriter(use_colors=True),
        error_log_writer,
        alert_writer
    )
    
    # Error logger
    error_logger = Logger(writer=error_multi_writer)
    
    # Example error scenarios
    try:
        # Simulate database error
        raise ConnectionError("Database connection failed")
    except ConnectionError as e:
        error_logger.error(
            "Database connection failed",
            error=str(e),
            component="database",
            retry_count=3,
            last_successful_connection="2023-01-01T10:00:00Z"
        )
    
    try:
        # Simulate validation error
        raise ValueError("Invalid user data")
    except ValueError as e:
        error_logger.warn(
            "Validation error",
            error=str(e),
            component="validation",
            user_input={"email": "invalid-email"}
        )


def performance_monitoring():
    """Performance monitoring setup."""
    print("\n=== Performance Monitoring ===")
    
    import time
    import functools
    
    # Performance logger
    perf_logger = production_logger_setup().with_context(type="performance")
    
    # Timing decorator
    def timed_operation(operation_name: str):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                perf_logger.info(
                    "Operation started",
                    operation=operation_name,
                    function=func.__name__
                )
                
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    perf_logger.info(
                        "Operation completed",
                        operation=operation_name,
                        function=func.__name__,
                        duration_ms=round(duration * 1000, 2),
                        status="success"
                    )
                    
                    return result
                    
                except Exception as e:
                    duration = time.time() - start_time
                    
                    perf_logger.error(
                        "Operation failed",
                        operation=operation_name,
                        function=func.__name__,
                        duration_ms=round(duration * 1000, 2),
                        error=str(e),
                        status="failed"
                    )
                    
                    raise
            
            return wrapper
        return decorator
    
    # Example usage
    @timed_operation("user_creation")
    def create_user(name: str, email: str):
        # Simulate work
        time.sleep(0.1)
        return {"id": "user-123", "name": name, "email": email}
    
    @timed_operation("database_query")
    def fetch_user_orders(user_id: str):
        # Simulate database query
        time.sleep(0.05)
        return [{"id": "order-1"}, {"id": "order-2"}]
    
    # Test performance monitoring
    user = create_user("John Doe", "john@example.com")
    orders = fetch_user_orders("user-123")


def log_filtering_setup():
    """Advanced log filtering setup."""
    print("\n=== Log Filtering Setup ===")
    
    base_logger = production_logger_setup()
    
    # Filter for sensitive operations
    sensitive_filter = FilterWriter(
        FileWriter("logs/sensitive.log"),
        predicate=lambda entry: entry.context.get("sensitive", False)
    )
    
    # Filter for specific users
    vip_user_filter = FilterWriter(
        FileWriter("logs/vip_users.log"),
        predicate=lambda entry: entry.context.get("user_type") == "vip"
    )
    
    # Filter for slow operations
    slow_operations_filter = FilterWriter(
        FileWriter("logs/slow_operations.log"),
        predicate=lambda entry: entry.context.get("duration_ms", 0) > 1000
    )
    
    # Multi-writer with filters
    filtered_writer = MultiWriter(
        ConsoleWriter(use_colors=True),
        sensitive_filter,
        vip_user_filter,
        slow_operations_filter
    )
    
    # Logger with filtering
    filtered_logger = Logger(writer=filtered_writer)
    
    # Example logs that will be filtered
    filtered_logger.info(
        "User login",
        user_id="user-123",
        sensitive=True,
        operation="password_change"
    )
    
    filtered_logger.info(
        "VIP user action",
        user_id="vip-456",
        user_type="vip",
        action="premium_feature_access"
    )
    
    filtered_logger.info(
        "Slow operation completed",
        operation="data_export",
        duration_ms=2500,
        records_processed=10000
    )


def log_rotation_setup():
    """Log rotation configuration."""
    print("\n=== Log Rotation Setup ===")
    
    # Custom rotating file writer
    class RotatingFileWriter:
        def __init__(self, base_path: str, max_size_mb: int = 10):
            self.base_path = Path(base_path)
            self.max_size_mb = max_size_mb
            self.current_file = None
            self.file_counter = 1
            
        def _get_current_file(self):
            if self.current_file is None:
                self.current_file = self.base_path
            
            # Check if rotation is needed
            if self.current_file.exists():
                size_mb = self.current_file.stat().st_size / (1024 * 1024)
                if size_mb >= self.max_size_mb:
                    # Rotate file
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    rotated_name = f"{self.base_path.stem}_{timestamp}.log"
                    rotated_path = self.base_path.parent / rotated_name
                    self.current_file.rename(rotated_path)
                    self.file_counter += 1
                    
            return self.current_file
        
        def write(self, entry):
            current_file = self._get_current_file()
            
            # Write to current file
            with open(current_file, "a", encoding="utf-8") as f:
                f.write(entry.to_json() + "\n")
    
    # Usage
    rotating_writer = RotatingFileWriter("logs/app_rotating.log", max_size_mb=1)
    rotating_logger = Logger(writer=rotating_writer)
    
    # Generate some logs
    for i in range(10):
        rotating_logger.info(f"Log entry {i}", iteration=i, data="x" * 1000)
    
    print("Log rotation configured")


if __name__ == "__main__":
    # Set up environment variables for testing
    os.environ.setdefault("ENV", "development")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    os.environ.setdefault("SERVICE_NAME", "example-service")
    os.environ.setdefault("SERVICE_VERSION", "1.0.0")
    
    production_logger_setup()
    microservice_logger()
    request_tracing_setup()
    error_handling_setup()
    performance_monitoring()
    log_filtering_setup()
    log_rotation_setup()
    
    print("\n=== Production Setup Examples Complete ===")
    print("Check logs/ directory for output files")