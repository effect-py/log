"""Basic usage examples for effect-log."""

from effect_log import Logger, LogLevel, with_context, with_span, with_writer
from effect_log.writers import ConsoleWriter, FileWriter, JSONConsoleWriter, MultiWriter


def basic_logging():
    """Basic logging example."""
    print("=== Basic Logging ===")
    
    # Simple logger
    logger = Logger()
    
    logger.info("Application started")
    logger.debug("Debug information")  # Won't show (below INFO level)
    logger.warn("Warning message")
    logger.error("Error occurred", error_code=500)
    logger.fatal("Fatal error", exception="OutOfMemoryError")


def functional_composition():
    """Functional composition example."""
    print("\n=== Functional Composition ===")
    
    # Using pipe for functional composition
    logger = Logger().pipe(
        with_context(service="user-service", version="1.2.3"),
        with_span("request-abc123", "trace-xyz789")
    )
    
    logger.info("User created", user_id="12345", email="user@example.com")
    logger.info("User updated", user_id="12345", action="profile_update")


def immutable_loggers():
    """Immutable logger example."""
    print("\n=== Immutable Loggers ===")
    
    # Base logger
    base_logger = Logger().with_context(service="api")
    
    # Create specialized loggers
    user_logger = base_logger.with_context(module="user")
    order_logger = base_logger.with_context(module="order")
    
    # Each logger maintains its own context
    user_logger.info("User operation", operation="create")
    order_logger.info("Order operation", operation="process")
    
    # Base logger is unchanged
    base_logger.info("Base operation")


def different_writers():
    """Different writer examples."""
    print("\n=== Different Writers ===")
    
    # Console writer with colors
    console_logger = Logger(writer=ConsoleWriter(use_colors=True))
    console_logger.info("Colored console output")
    console_logger.error("Error with colors")
    
    # JSON console writer
    json_logger = Logger(writer=JSONConsoleWriter())
    json_logger.info("JSON structured output", user_id="123", action="login")
    
    # File writer
    file_logger = Logger(writer=FileWriter("app.log"))
    file_logger.info("This goes to file", module="auth", user="john")
    
    # Multi-writer (console + file)
    multi_writer = MultiWriter(
        ConsoleWriter(use_colors=False),
        FileWriter("combined.log")
    )
    multi_logger = Logger(writer=multi_writer)
    multi_logger.info("This goes to both console and file")


def context_management():
    """Context management examples."""
    print("\n=== Context Management ===")
    
    # Build context gradually
    logger = Logger()
    
    # Add service context
    service_logger = logger.with_context(service="payment-service")
    
    # Add request context
    request_logger = service_logger.with_context(
        request_id="req-123",
        user_id="user-456"
    )
    
    # Add span context
    span_logger = request_logger.with_span("payment-process", "trace-789")
    
    # Log with full context
    span_logger.info("Payment processing started", amount=99.99, currency="USD")
    span_logger.info("Payment validation passed")
    span_logger.info("Payment completed", transaction_id="txn-abc123")


def log_levels():
    """Log level examples."""
    print("\n=== Log Levels ===")
    
    # Create loggers with different minimum levels
    debug_logger = Logger(min_level=LogLevel.DEBUG)
    warn_logger = Logger(min_level=LogLevel.WARN)
    
    print("Debug logger (shows all levels):")
    debug_logger.trace("Trace message")
    debug_logger.debug("Debug message")
    debug_logger.info("Info message")
    debug_logger.warn("Warning message")
    debug_logger.error("Error message")
    
    print("\nWarn logger (shows only WARN and above):")
    warn_logger.trace("Trace message")
    warn_logger.debug("Debug message")
    warn_logger.info("Info message")
    warn_logger.warn("Warning message")
    warn_logger.error("Error message")


def chaining_operations():
    """Chaining operations example."""
    print("\n=== Chaining Operations ===")
    
    # Start with base logger
    base_logger = Logger()
    
    # Chain operations to create specialized logger
    api_logger = (base_logger
                  .with_context(service="api-gateway")
                  .with_context(version="2.1.0")
                  .with_span("api-request")
                  .with_min_level(LogLevel.INFO))
    
    api_logger.info("API request received", endpoint="/users", method="GET")
    api_logger.info("API response sent", status_code=200, duration_ms=45)


def error_logging():
    """Error logging with context."""
    print("\n=== Error Logging ===")
    
    logger = Logger().with_context(service="data-processor")
    
    try:
        # Simulate some operation
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error(
            "Division by zero error",
            error=str(e),
            operation="calculate_average",
            input_data=[1, 2, 3, 0]
        )
    
    try:
        # Simulate another operation
        data = {"key": "value"}
        missing_key = data["missing"]
    except KeyError as e:
        logger.error(
            "Missing key error",
            error=str(e),
            operation="data_access",
            available_keys=list(data.keys())
        )


if __name__ == "__main__":
    basic_logging()
    functional_composition()
    immutable_loggers()
    different_writers()
    context_management()
    log_levels()
    chaining_operations()
    error_logging()
    
    print("\n=== Example Complete ===")
    print("Check app.log and combined.log for file output")