"""Tests for middleware module."""

import time
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from effect_log import Logger, LogLevel
from effect_log.middleware import HttpLoggerMiddleware


class MockRequest:
    """Mock HTTP request for testing."""
    
    def __init__(self, method="GET", path="/", query_string="", **kwargs):
        self.method = method
        self.path = path
        self.query_string = query_string
        self.headers = kwargs.get("headers", {})
        self.remote_addr = kwargs.get("remote_addr", "127.0.0.1")
        self.body = kwargs.get("body", "")
        self.data = kwargs.get("data", "")


class MockResponse:
    """Mock HTTP response for testing."""
    
    def __init__(self, status_code=200, **kwargs):
        self.status_code = status_code
        self.headers = kwargs.get("headers", {})
        self.body = kwargs.get("body", "")
        self.content = kwargs.get("content", "")


class TestHttpLoggerMiddleware:
    """Test suite for HttpLoggerMiddleware."""
    
    def test_middleware_basic_request(self):
        """Test basic request processing."""
        writer = Mock()
        logger = Logger(writer=writer)
        middleware = HttpLoggerMiddleware(logger)
        
        request = MockRequest(method="GET", path="/api/users")
        result = middleware(request)
        
        assert "logger" in result
        assert "request_id" in result
        assert "start_time" in result
        
        # Check that request was logged
        writer.write.assert_called_once()
        entry = writer.write.call_args[0][0]
        assert entry.message == "HTTP request"
        assert entry.context["request_id"] == result["request_id"]
        assert entry.context["http_method"] == "GET"
        assert entry.context["http_path"] == "/api/users"
    
    def test_middleware_request_response(self):
        """Test request and response processing."""
        writer = Mock()
        logger = Logger(writer=writer)
        middleware = HttpLoggerMiddleware(logger)
        
        request = MockRequest(method="POST", path="/api/users")
        response = MockResponse(status_code=201)
        
        result = middleware(request, response)
        
        # Should have logged both request and response
        assert writer.write.call_count == 2
        
        # Check request log
        request_entry = writer.write.call_args_list[0][0][0]
        assert request_entry.message == "HTTP request"
        assert request_entry.context["http_method"] == "POST"
        
        # Check response log
        response_entry = writer.write.call_args_list[1][0][0]
        assert response_entry.message == "HTTP response"
        assert response_entry.context["http_status"] == 201
        assert "duration_ms" in response_entry.context
    
    def test_middleware_with_headers(self):
        """Test middleware with header logging enabled."""
        writer = Mock()
        logger = Logger(writer=writer)
        middleware = HttpLoggerMiddleware(logger, include_headers=True)
        
        request = MockRequest(
            method="GET",
            path="/api/users",
            headers={"Authorization": "Bearer token", "Content-Type": "application/json"}
        )
        
        middleware(request)
        
        writer.write.assert_called_once()
        entry = writer.write.call_args[0][0]
        assert "headers" in entry.context
        assert entry.context["headers"]["Authorization"] == "Bearer token"
        assert entry.context["headers"]["Content-Type"] == "application/json"
    
    def test_middleware_with_body(self):
        """Test middleware with body logging enabled."""
        writer = Mock()
        logger = Logger(writer=writer)
        middleware = HttpLoggerMiddleware(logger, include_body=True)
        
        request = MockRequest(
            method="POST",
            path="/api/users",
            body='{"name": "John", "email": "john@example.com"}'
        )
        
        middleware(request)
        
        writer.write.assert_called_once()
        entry = writer.write.call_args[0][0]
        assert "body" in entry.context
        assert '"name": "John"' in entry.context["body"]
    
    def test_middleware_body_truncation(self):
        """Test body truncation for large bodies."""
        writer = Mock()
        logger = Logger(writer=writer)
        middleware = HttpLoggerMiddleware(logger, include_body=True, max_body_size=10)
        
        request = MockRequest(
            method="POST",
            path="/api/users",
            body="This is a very long body that should be truncated"
        )
        
        middleware(request)
        
        writer.write.assert_called_once()
        entry = writer.write.call_args[0][0]
        assert entry.context["body"] == "This is a ..."
    
    def test_middleware_excluded_paths(self):
        """Test path exclusion functionality."""
        writer = Mock()
        logger = Logger(writer=writer)
        middleware = HttpLoggerMiddleware(logger, exclude_paths=["/health", "/metrics"])
        
        # Request to excluded path
        health_request = MockRequest(path="/health")
        result = middleware(health_request)
        
        # Should not log the request
        writer.write.assert_not_called()
        
        # Should still return logger context
        assert "logger" in result
        assert "request_id" in result
        
        # Request to non-excluded path
        api_request = MockRequest(path="/api/users")
        middleware(api_request)
        
        # Should log this request
        writer.write.assert_called_once()
    
    def test_middleware_response_log_levels(self):
        """Test response log levels based on status codes."""
        writer = Mock()
        logger = Logger(writer=writer)
        middleware = HttpLoggerMiddleware(logger)
        
        request = MockRequest()
        
        # Test different status codes
        test_cases = [
            (200, LogLevel.INFO),
            (201, LogLevel.INFO),
            (400, LogLevel.WARN),
            (404, LogLevel.WARN),
            (500, LogLevel.ERROR),
            (503, LogLevel.ERROR)
        ]
        
        for status_code, expected_level in test_cases:
            writer.reset_mock()
            response = MockResponse(status_code=status_code)
            middleware(request, response)
            
            # Should log response
            writer.write.assert_called()
            entry = writer.write.call_args[0][0]
            assert entry.level == expected_level
    
    def test_middleware_request_disable_logging(self):
        """Test disabling request logging."""
        writer = Mock()
        logger = Logger(writer=writer)
        middleware = HttpLoggerMiddleware(logger, log_requests=False)
        
        request = MockRequest()
        middleware(request)
        
        # Should not log request
        writer.write.assert_not_called()
    
    def test_middleware_response_disable_logging(self):
        """Test disabling response logging."""
        writer = Mock()
        logger = Logger(writer=writer)
        middleware = HttpLoggerMiddleware(logger, log_responses=False)
        
        request = MockRequest()
        response = MockResponse()
        middleware(request, response)
        
        # Should only log request, not response
        writer.write.assert_called_once()
        entry = writer.write.call_args[0][0]
        assert entry.message == "HTTP request"
    
    def test_middleware_binary_body_handling(self):
        """Test handling of binary body content."""
        writer = Mock()
        logger = Logger(writer=writer)
        middleware = HttpLoggerMiddleware(logger, include_body=True)
        
        # Binary content that can't be decoded
        binary_body = b'\x80\x81\x82\x83'
        request = MockRequest(method="POST", path="/api/upload", body=binary_body)
        
        middleware(request)
        
        writer.write.assert_called_once()
        entry = writer.write.call_args[0][0]
        assert entry.context["body"] == "<binary data>"
    
    def test_middleware_missing_attributes(self):
        """Test middleware with objects missing expected attributes."""
        writer = Mock()
        logger = Logger(writer=writer)
        middleware = HttpLoggerMiddleware(logger)
        
        # Create minimal request object
        minimal_request = type('Request', (), {})()
        
        result = middleware(minimal_request)
        
        # Should still work with defaults
        assert "logger" in result
        writer.write.assert_called_once()
        entry = writer.write.call_args[0][0]
        assert entry.context["http_method"] == "UNKNOWN"
        assert entry.context["http_path"] == "/"
    
    def test_middleware_context_propagation(self):
        """Test that middleware preserves existing logger context."""
        writer = Mock()
        base_logger = Logger(writer=writer).with_context(service="api", version="1.0")
        middleware = HttpLoggerMiddleware(base_logger)
        
        request = MockRequest(method="GET", path="/api/users")
        result = middleware(request)
        
        # Check that original context is preserved
        request_logger = result["logger"]
        writer.write.assert_called_once()
        entry = writer.write.call_args[0][0]
        assert entry.context["service"] == "api"
        assert entry.context["version"] == "1.0"
        assert entry.context["http_method"] == "GET"
    
    @patch('effect_log.middleware.time.time')
    def test_middleware_duration_calculation(self, mock_time):
        """Test duration calculation for responses."""
        mock_time.side_effect = [1000.0, 1001.5]  # 1.5 second duration
        
        writer = Mock()
        logger = Logger(writer=writer)
        middleware = HttpLoggerMiddleware(logger)
        
        request = MockRequest()
        response = MockResponse()
        
        middleware(request, response)
        
        # Should log response with duration
        assert writer.write.call_count == 2
        response_entry = writer.write.call_args_list[1][0][0]
        assert response_entry.context["duration_ms"] == 1500.0