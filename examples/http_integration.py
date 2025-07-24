"""HTTP integration examples for effect-log."""

from effect_log import Logger, LogLevel
from effect_log.middleware import HttpLoggerMiddleware
from effect_log.writers import ConsoleWriter, FileWriter, JSONConsoleWriter, MultiWriter


def flask_example():
    """Flask integration example."""
    print("=== Flask Integration Example ===")

    try:
        from flask import Flask, g, request

        app = Flask(__name__)

        # Create logger with multiple writers
        logger = Logger(
            writer=MultiWriter(
                ConsoleWriter(use_colors=True), FileWriter("flask_app.log")
            )
        ).with_context(service="flask-api", version="1.0.0")

        # Create middleware
        middleware = HttpLoggerMiddleware(
            logger, include_headers=True, exclude_paths=["/health", "/metrics"]
        )

        @app.before_request
        def before_request():
            result = middleware(request)
            g.logger = result["logger"]
            g.request_id = result["request_id"]
            g.start_time = result["start_time"]

        @app.after_request
        def after_request(response):
            if hasattr(g, "logger") and hasattr(g, "start_time"):
                import time

                duration = time.time() - g.start_time
                middleware._log_response(g.logger, response, duration)
            return response

        @app.route("/users/<user_id>")
        def get_user(user_id):
            # Use logger from middleware
            g.logger.info("Fetching user", user_id=user_id)

            # Simulate some business logic
            if user_id == "123":
                g.logger.info("User found", user_id=user_id, name="John Doe")
                return {"id": user_id, "name": "John Doe"}
            else:
                g.logger.warn("User not found", user_id=user_id)
                return {"error": "User not found"}, 404

        @app.route("/orders", methods=["POST"])
        def create_order():
            # Create order-specific logger
            order_logger = g.logger.with_context(operation="create_order")

            order_logger.info("Order creation started")

            # Simulate order processing
            order_id = "order-12345"
            order_logger.info("Order created", order_id=order_id, amount=99.99)

            return {"order_id": order_id, "status": "created"}

        @app.route("/health")
        def health():
            # This won't be logged due to exclude_paths
            return {"status": "healthy"}

        print("Flask app configured with effect-log middleware")
        print("Routes available:")
        print("  GET /users/<user_id>")
        print("  POST /orders")
        print("  GET /health (not logged)")

    except ImportError:
        print("Flask not available - install with: pip install flask")


def fastapi_example():
    """FastAPI integration example."""
    print("\n=== FastAPI Integration Example ===")

    try:
        import time

        from fastapi import FastAPI, HTTPException, Request

        app = FastAPI()

        # Create logger
        logger = Logger(writer=JSONConsoleWriter()).with_context(
            service="fastapi-api", version="2.0.0"
        )

        # Create middleware
        middleware = HttpLoggerMiddleware(
            logger,
            include_headers=True,
            include_body=True,
            exclude_paths=["/docs", "/openapi.json"],
        )

        @app.middleware("http")
        async def logging_middleware(request: Request, call_next):
            result = middleware(request)
            request_logger = result["logger"]
            start_time = result["start_time"]

            # Add logger to request state
            request.state.logger = request_logger
            request.state.request_id = result["request_id"]

            try:
                response = await call_next(request)

                # Log response
                duration = time.time() - start_time
                middleware._log_response(request_logger, response, duration)

                return response

            except Exception as e:
                # Log exception
                request_logger.error(
                    "Request failed", error=str(e), exception=type(e).__name__
                )
                raise

        @app.get("/users/{user_id}")
        async def get_user(user_id: str, request: Request):
            logger = request.state.logger
            logger.info("Fetching user", user_id=user_id)

            if user_id == "123":
                logger.info("User found", user_id=user_id)
                return {"id": user_id, "name": "Alice Smith"}
            else:
                logger.warn("User not found", user_id=user_id)
                raise HTTPException(status_code=404, detail="User not found")

        @app.post("/orders")
        async def create_order(request: Request, order_data: dict):
            logger = request.state.logger.with_context(operation="create_order")

            logger.info("Order creation started", order_data=order_data)

            # Simulate validation
            if "amount" not in order_data:
                logger.error("Invalid order data", missing_field="amount")
                raise HTTPException(status_code=400, detail="Amount is required")

            order_id = "order-67890"
            logger.info("Order created", order_id=order_id, amount=order_data["amount"])

            return {"order_id": order_id, "status": "created"}

        print("FastAPI app configured with effect-log middleware")
        print("Routes available:")
        print("  GET /users/{user_id}")
        print("  POST /orders")
        print("  GET /docs (not logged)")

    except ImportError:
        print("FastAPI not available - install with: pip install fastapi")


def django_example():
    """Django integration example."""
    print("\n=== Django Integration Example ===")

    print("Django middleware configuration:")
    print(
        """
# In settings.py
MIDDLEWARE = [
    'effect_log.middleware.DjangoMiddleware',
    # ... other middleware
]

# In views.py
from effect_log import Logger
from effect_log.writers import FileWriter

logger = Logger(writer=FileWriter('django_app.log'))

def user_view(request):
    # Logger is available on request object
    request.logger.info("User view accessed", user_id=request.user.id)

    # Create operation-specific logger
    operation_logger = request.logger.with_context(
        operation="user_profile_update"
    )

    operation_logger.info("Profile update started")
    # ... business logic
    operation_logger.info("Profile update completed")

    return JsonResponse({"status": "success"})
"""
    )


def custom_middleware_example():
    """Custom middleware implementation example."""
    print("\n=== Custom Middleware Example ===")

    # Create a custom middleware for any framework
    class CustomFrameworkMiddleware:
        def __init__(self, logger: Logger):
            self.http_middleware = HttpLoggerMiddleware(
                logger, include_headers=True, exclude_paths=["/internal"]
            )

        def process_request(self, request):
            """Process incoming request."""
            result = self.http_middleware(request)

            # Store logger in request for later use
            request.effect_logger = result["logger"]
            request.effect_request_id = result["request_id"]
            request.effect_start_time = result["start_time"]

            return result

        def process_response(self, request, response):
            """Process outgoing response."""
            if hasattr(request, "effect_logger"):
                import time

                duration = time.time() - request.effect_start_time
                self.http_middleware._log_response(
                    request.effect_logger, response, duration
                )

            return response

    # Usage example
    logger = Logger().with_context(service="custom-framework")
    CustomFrameworkMiddleware(logger)

    print("Custom middleware created")
    print("Use process_request() and process_response() in your framework")


def structured_logging_example():
    """Structured logging in HTTP context."""
    print("\n=== Structured Logging Example ===")

    # Create base logger
    base_logger = Logger(writer=JSONConsoleWriter(), min_level=LogLevel.INFO)

    # Simulate HTTP request processing
    class MockRequest:
        def __init__(self, method, path, user_id=None):
            self.method = method
            self.path = path
            self.user_id = user_id

    def process_request(request):
        # Create request-specific logger
        request_logger = base_logger.pipe(
            lambda logger: logger.with_context(
                http_method=request.method,
                http_path=request.path,
                request_id=f"req-{hash(request) % 10000}",
            ),
            lambda logger: (
                logger.with_context(user_id=request.user_id)
                if request.user_id
                else logger
            ),
        )

        request_logger.info("Request started")

        # Simulate business logic with different contexts
        if request.path.startswith("/api/users"):
            user_logger = request_logger.with_context(module="user_service")
            user_logger.info("User operation", operation="fetch")

            if request.user_id:
                user_logger.info("User authorized", user_id=request.user_id)
            else:
                user_logger.warn("Unauthorized access attempt")

        elif request.path.startswith("/api/orders"):
            order_logger = request_logger.with_context(module="order_service")
            order_logger.info("Order operation", operation="create")

            # Simulate order processing steps
            order_logger.info("Order validation started")
            order_logger.info("Order validation passed")
            order_logger.info("Order saved to database")

        request_logger.info("Request completed", status_code=200)

    # Process different requests
    requests = [
        MockRequest("GET", "/api/users/123", user_id="user-123"),
        MockRequest("POST", "/api/orders", user_id="user-456"),
        MockRequest("GET", "/api/users/456"),  # No user_id
    ]

    for req in requests:
        process_request(req)
        print()


if __name__ == "__main__":
    flask_example()
    fastapi_example()
    django_example()
    custom_middleware_example()
    structured_logging_example()

    print("\n=== HTTP Integration Examples Complete ===")
    print("Check flask_app.log for Flask output")
