"""HTTP middleware for effect-log functional structured logging."""

from __future__ import annotations

import time
import uuid
from typing import Any

from .logger import Logger
from .types import LogLevel


class HttpLoggerMiddleware:
    """HTTP middleware for request/response logging."""

    def __init__(
        self,
        logger: Logger,
        log_requests: bool = True,
        log_responses: bool = True,
        include_headers: bool = False,
        include_body: bool = False,
        max_body_size: int = 1024,
        exclude_paths: list[str] | None = None,
    ):
        self.logger = logger
        self.log_requests = log_requests
        self.log_responses = log_responses
        self.include_headers = include_headers
        self.include_body = include_body
        self.max_body_size = max_body_size
        self.exclude_paths = exclude_paths or []

    def __call__(self, request: Any, response: Any = None) -> dict[str, Any]:
        """Process HTTP request/response and return context."""
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Create logger with request context
        request_logger = self.logger.with_context(
            request_id=request_id,
            http_method=getattr(request, "method", "UNKNOWN"),
            http_path=getattr(request, "path", "/"),
            http_query=getattr(request, "query_string", ""),
            user_agent=self._get_header(request, "user-agent"),
            remote_addr=getattr(request, "remote_addr", None),
        )

        # Skip logging for excluded paths
        path = getattr(request, "path", "/")
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            return {"logger": request_logger, "request_id": request_id}

        # Log request
        if self.log_requests:
            self._log_request(request_logger, request)

        # Log response if provided
        if response is not None and self.log_responses:
            duration = time.time() - start_time
            self._log_response(request_logger, response, duration)

        return {
            "logger": request_logger,
            "request_id": request_id,
            "start_time": start_time,
        }

    def _log_request(self, logger: Logger, request: Any) -> None:
        """Log HTTP request."""
        context: dict[str, Any] = {}

        if self.include_headers:
            context["headers"] = self._get_headers(request)

        if self.include_body:
            body = self._get_body(request)
            if body:
                context["request_body"] = body

        logger.info("HTTP request", **context)

    def _log_response(self, logger: Logger, response: Any, duration: float) -> None:
        """Log HTTP response."""
        status_code = getattr(response, "status_code", 200)

        context = {"http_status": status_code, "duration_ms": round(duration * 1000, 2)}

        if self.include_headers:
            context["response_headers"] = self._get_headers(response)

        if self.include_body:
            body = self._get_body(response)
            if body:
                context["response_body"] = body

        # Choose log level based on status code
        level = self._get_log_level_for_status(status_code)
        logger.log(level, "HTTP response", **context)

    def _get_header(self, obj: Any, header_name: str) -> str | None:
        """Get header value from request/response object."""
        if hasattr(obj, "headers"):
            headers = obj.headers
            if hasattr(headers, "get"):
                return (
                    str(headers.get(header_name)) if headers.get(header_name) else None
                )
            elif isinstance(headers, dict):
                return (
                    str(headers.get(header_name)) if headers.get(header_name) else None
                )
        return None

    def _get_headers(self, obj: Any) -> dict[str, str]:
        """Get all headers from request/response object."""
        if hasattr(obj, "headers"):
            headers = obj.headers
            if hasattr(headers, "items"):
                return dict(headers.items())
            elif isinstance(headers, dict):
                return headers
        return {}

    def _get_body(self, obj: Any) -> str | None:
        """Get body from request/response object."""
        body = None

        # Try different ways to get body
        if hasattr(obj, "body"):
            body = obj.body
        elif hasattr(obj, "data"):
            body = obj.data
        elif hasattr(obj, "content"):
            body = obj.content

        if body is None:
            return None

        # Convert to string if needed
        if isinstance(body, bytes):
            try:
                body = body.decode("utf-8")
            except UnicodeDecodeError:
                return "<binary data>"
        elif not isinstance(body, str):
            body = str(body)

        # Truncate if too long
        if len(body) > self.max_body_size:
            body = body[: self.max_body_size] + "..."

        return str(body)

    def _get_log_level_for_status(self, status_code: int) -> LogLevel:
        """Determine log level based on HTTP status code."""
        if status_code >= 500:
            return LogLevel.ERROR
        elif status_code >= 400:
            return LogLevel.WARN
        else:
            return LogLevel.INFO


# Framework-specific middleware implementations


class FlaskMiddleware:
    """Flask-specific HTTP logging middleware."""

    def __init__(self, middleware: HttpLoggerMiddleware):
        self.middleware = middleware

    def __call__(self, app: Any) -> Any:
        """Apply middleware to Flask app."""

        @app.before_request
        def log_request() -> None:
            from flask import g, request

            result = self.middleware(request)
            g.logger = result["logger"]
            g.request_id = result["request_id"]
            g.start_time = result["start_time"]

        @app.after_request
        def log_response(response: Any) -> Any:
            from flask import g

            if hasattr(g, "logger") and hasattr(g, "start_time"):
                duration = time.time() - g.start_time
                self.middleware._log_response(g.logger, response, duration)
            return response

        return app


class FastAPIMiddleware:
    """FastAPI-specific HTTP logging middleware."""

    def __init__(self, middleware: HttpLoggerMiddleware):
        self.middleware = middleware

    async def __call__(self, request: Any, call_next: Any) -> Any:
        """Apply middleware to FastAPI request."""
        result = self.middleware(request)
        logger = result["logger"]
        start_time = result["start_time"]

        # Add logger to request state
        request.state.logger = logger
        request.state.request_id = result["request_id"]

        # Process request
        response = await call_next(request)

        # Log response
        duration = time.time() - start_time
        self.middleware._log_response(logger, response, duration)

        return response


class DjangoMiddleware:
    """Django-specific HTTP logging middleware."""

    def __init__(self, get_response: Any, middleware: HttpLoggerMiddleware) -> None:
        self.get_response = get_response
        self.middleware = middleware

    def __call__(self, request: Any) -> Any:
        """Apply middleware to Django request."""
        result = self.middleware(request)
        request.logger = result["logger"]
        request.request_id = result["request_id"]
        start_time = result["start_time"]

        response = self.get_response(request)

        duration = time.time() - start_time
        self.middleware._log_response(request.logger, response, duration)

        return response
