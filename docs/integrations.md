# Framework Integration Guide

This guide provides detailed instructions for integrating effect-log with popular Python web frameworks.

## Table of Contents

- [Flask Integration](#flask-integration)
- [FastAPI Integration](#fastapi-integration)
- [Django Integration](#django-integration)
- [Starlette Integration](#starlette-integration)
- [Custom Framework Integration](#custom-framework-integration)
- [ASGI/WSGI Integration](#asgiwsgi-integration)

## Flask Integration

### Basic Setup

```python
from flask import Flask, request, g
from effect_log import Logger
from effect_log.middleware import HttpLoggerMiddleware
from effect_log.writers import JSONConsoleWriter

app = Flask(__name__)

# Create logger
logger = Logger(
    writer=JSONConsoleWriter(),
    min_level=LogLevel.INFO
).with_context(service="flask-api", version="1.0.0")

# Create middleware
middleware = HttpLoggerMiddleware(
    logger,
    include_headers=True,
    exclude_paths=["/health", "/metrics"]
)

@app.before_request
def before_request():
    result = middleware(request)
    g.logger = result["logger"]
    g.request_id = result["request_id"]
    g.start_time = result["start_time"]

@app.after_request
def after_request(response):
    if hasattr(g, 'logger') and hasattr(g, 'start_time'):
        import time
        duration = time.time() - g.start_time
        middleware._log_response(g.logger, response, duration)
    return response
```

### Route-Level Logging

```python
@app.route("/users/<user_id>")
def get_user(user_id):
    # Use logger from middleware
    user_logger = g.logger.with_context(user_id=user_id)
    user_logger.info("Fetching user")
    
    try:
        user = get_user_from_db(user_id)
        user_logger.info("User found", user_name=user.name)
        return {"user": user.to_dict()}
    except UserNotFound:
        user_logger.warn("User not found")
        return {"error": "User not found"}, 404
    except Exception as e:
        user_logger.error("Error fetching user", error=str(e))
        return {"error": "Internal server error"}, 500

@app.route("/orders", methods=["POST"])
def create_order():
    order_logger = g.logger.with_context(operation="create_order")
    order_logger.info("Creating order", data=request.json)
    
    try:
        order = create_order_in_db(request.json)
        order_logger.info("Order created", order_id=order.id)
        return {"order": order.to_dict()}, 201
    except ValidationError as e:
        order_logger.warn("Invalid order data", errors=e.errors)
        return {"error": "Validation failed", "details": e.errors}, 400
```

### Error Handling

```python
@app.errorhandler(Exception)
def handle_exception(e):
    if hasattr(g, 'logger'):
        g.logger.error("Unhandled exception", 
            error=str(e),
            error_type=type(e).__name__,
            path=request.path,
            method=request.method
        )
    return {"error": "Internal server error"}, 500

@app.errorhandler(404)
def handle_not_found(e):
    if hasattr(g, 'logger'):
        g.logger.warn("Resource not found", path=request.path)
    return {"error": "Not found"}, 404
```

### Flask Extension

Create a Flask extension for easier integration:

```python
from flask import Flask, g
from effect_log import Logger
from effect_log.middleware import HttpLoggerMiddleware

class EffectLog:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        app.config.setdefault('EFFECT_LOG_LEVEL', 'INFO')
        app.config.setdefault('EFFECT_LOG_INCLUDE_HEADERS', False)
        app.config.setdefault('EFFECT_LOG_EXCLUDE_PATHS', [])
        
        # Create logger
        logger = Logger(
            min_level=getattr(LogLevel, app.config['EFFECT_LOG_LEVEL'])
        ).with_context(service=app.name)
        
        # Create middleware
        middleware = HttpLoggerMiddleware(
            logger,
            include_headers=app.config['EFFECT_LOG_INCLUDE_HEADERS'],
            exclude_paths=app.config['EFFECT_LOG_EXCLUDE_PATHS']
        )
        
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
        app.extensions['effect_log'] = {
            'logger': logger,
            'middleware': middleware
        }
    
    def _before_request(self):
        middleware = current_app.extensions['effect_log']['middleware']
        result = middleware(request)
        g.logger = result["logger"]
        g.request_id = result["request_id"]
        g.start_time = result["start_time"]
    
    def _after_request(self, response):
        if hasattr(g, 'logger') and hasattr(g, 'start_time'):
            import time
            middleware = current_app.extensions['effect_log']['middleware']
            duration = time.time() - g.start_time
            middleware._log_response(g.logger, response, duration)
        return response

# Usage
app = Flask(__name__)
effect_log = EffectLog(app)
```

## FastAPI Integration

### Basic Setup

```python
from fastapi import FastAPI, Request
from effect_log import Logger
from effect_log.middleware import HttpLoggerMiddleware
from effect_log.writers import JSONConsoleWriter
import time

app = FastAPI()

# Create logger
logger = Logger(
    writer=JSONConsoleWriter(),
    min_level=LogLevel.INFO
).with_context(service="fastapi-api", version="1.0.0")

# Create middleware
http_middleware = HttpLoggerMiddleware(
    logger,
    include_headers=True,
    exclude_paths=["/docs", "/openapi.json", "/health"]
)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    result = http_middleware(request)
    request_logger = result["logger"]
    start_time = result["start_time"]
    
    # Add logger to request state
    request.state.logger = request_logger
    request.state.request_id = result["request_id"]
    
    try:
        response = await call_next(request)
        
        # Log response
        duration = time.time() - start_time
        http_middleware._log_response(request_logger, response, duration)
        
        return response
    except Exception as e:
        request_logger.error("Request failed", 
            error=str(e),
            error_type=type(e).__name__
        )
        raise
```

### Route-Level Logging

```python
from fastapi import HTTPException
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str

@app.get("/users/{user_id}")
async def get_user(user_id: str, request: Request):
    logger = request.state.logger.with_context(user_id=user_id)
    logger.info("Fetching user")
    
    try:
        user = await get_user_from_db(user_id)
        logger.info("User found", user_name=user.name)
        return {"user": user.dict()}
    except UserNotFound:
        logger.warn("User not found")
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error("Error fetching user", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/users")
async def create_user(user_data: UserCreate, request: Request):
    logger = request.state.logger.with_context(operation="create_user")
    logger.info("Creating user", data=user_data.dict())
    
    try:
        user = await create_user_in_db(user_data)
        logger.info("User created", user_id=user.id)
        return {"user": user.dict()}
    except ValidationError as e:
        logger.warn("Invalid user data", errors=str(e))
        raise HTTPException(status_code=400, detail="Validation failed")
```

### Exception Handling

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    if hasattr(request.state, 'logger'):
        request.state.logger.error("Unhandled exception",
            error=str(exc),
            error_type=type(exc).__name__,
            path=request.url.path,
            method=request.method
        )
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if hasattr(request.state, 'logger'):
        request.state.logger.warn("HTTP exception",
            status_code=exc.status_code,
            detail=exc.detail,
            path=request.url.path
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )
```

### FastAPI Dependency

Create a dependency for easier logger access:

```python
from fastapi import Depends, Request

def get_logger(request: Request):
    return request.state.logger

@app.get("/users/{user_id}")
async def get_user(user_id: str, logger=Depends(get_logger)):
    logger.info("Fetching user", user_id=user_id)
    # ... rest of the function
```

## Django Integration

### Settings Configuration

```python
# settings.py
MIDDLEWARE = [
    'effect_log.middleware.DjangoMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... other middleware
]

# Effect-log configuration
EFFECT_LOG_CONFIG = {
    'service': 'django-app',
    'version': '1.0.0',
    'include_headers': True,
    'exclude_paths': ['/admin/', '/static/', '/media/'],
    'min_level': 'INFO',
}
```

### Custom Django Middleware

```python
# middleware.py
from django.utils.deprecation import MiddlewareMixin
from effect_log import Logger, LogLevel
from effect_log.middleware import HttpLoggerMiddleware
from effect_log.writers import JSONConsoleWriter
import time

class EffectLogMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Create logger
        logger = Logger(
            writer=JSONConsoleWriter(),
            min_level=LogLevel.INFO
        ).with_context(service="django-app")
        
        # Create HTTP middleware
        self.http_middleware = HttpLoggerMiddleware(
            logger,
            include_headers=True,
            exclude_paths=['/admin/', '/static/']
        )
        
        super().__init__(get_response)
    
    def process_request(self, request):
        result = self.http_middleware(request)
        request.logger = result["logger"]
        request.request_id = result["request_id"]
        request.start_time = result["start_time"]
    
    def process_response(self, request, response):
        if hasattr(request, 'logger') and hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            self.http_middleware._log_response(request.logger, response, duration)
        return response
```

### View-Level Logging

```python
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@require_http_methods(["GET"])
def get_user(request, user_id):
    logger = request.logger.with_context(user_id=user_id)
    logger.info("Fetching user")
    
    try:
        user = User.objects.get(id=user_id)
        logger.info("User found", user_name=user.name)
        return JsonResponse({"user": {"id": user.id, "name": user.name}})
    except User.DoesNotExist:
        logger.warn("User not found")
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        logger.error("Error fetching user", error=str(e))
        return JsonResponse({"error": "Internal server error"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_user(request):
    logger = request.logger.with_context(operation="create_user")
    
    try:
        data = json.loads(request.body)
        logger.info("Creating user", data=data)
        
        user = User.objects.create(
            name=data["name"],
            email=data["email"]
        )
        logger.info("User created", user_id=user.id)
        return JsonResponse({"user": {"id": user.id, "name": user.name}})
    except Exception as e:
        logger.error("Error creating user", error=str(e))
        return JsonResponse({"error": "Internal server error"}, status=500)
```

### Django REST Framework Integration

```python
# serializers.py
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email']

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class UserViewSet(APIView):
    def get(self, request, user_id=None):
        logger = request.logger.with_context(user_id=user_id)
        logger.info("Fetching user")
        
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)
            logger.info("User found", user_name=user.name)
            return Response(serializer.data)
        except User.DoesNotExist:
            logger.warn("User not found")
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def post(self, request):
        logger = request.logger.with_context(operation="create_user")
        logger.info("Creating user", data=request.data)
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info("User created", user_id=user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.warn("Invalid user data", errors=serializer.errors)
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
```

## Starlette Integration

### Basic Setup

```python
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import JSONResponse
from effect_log import Logger
from effect_log.middleware import HttpLoggerMiddleware
import time

# Create logger
logger = Logger().with_context(service="starlette-api")

# Create HTTP middleware
http_middleware = HttpLoggerMiddleware(logger)

async def logging_middleware(request, call_next):
    result = http_middleware(request)
    request.state.logger = result["logger"]
    request.state.request_id = result["request_id"]
    start_time = result["start_time"]
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    http_middleware._log_response(request.state.logger, response, duration)
    
    return response

app = Starlette(middleware=[
    Middleware(logging_middleware)
])
```

### Route Handlers

```python
from starlette.routing import Route

async def get_user(request):
    user_id = request.path_params["user_id"]
    logger = request.state.logger.with_context(user_id=user_id)
    logger.info("Fetching user")
    
    try:
        user = await get_user_from_db(user_id)
        logger.info("User found", user_name=user.name)
        return JSONResponse({"user": user.dict()})
    except UserNotFound:
        logger.warn("User not found")
        return JSONResponse({"error": "User not found"}, status_code=404)

routes = [
    Route("/users/{user_id}", get_user, methods=["GET"]),
]

app = Starlette(routes=routes, middleware=[
    Middleware(logging_middleware)
])
```

## Custom Framework Integration

### Generic WSGI Integration

```python
from effect_log import Logger
from effect_log.middleware import HttpLoggerMiddleware
import time

class EffectLogWSGIMiddleware:
    def __init__(self, app, logger=None):
        self.app = app
        self.logger = logger or Logger()
        self.http_middleware = HttpLoggerMiddleware(self.logger)
    
    def __call__(self, environ, start_response):
        # Create mock request object
        request = self._create_request(environ)
        
        # Process request
        result = self.http_middleware(request)
        logger = result["logger"]
        start_time = result["start_time"]
        
        # Store in environ for access by application
        environ['effect_log.logger'] = logger
        environ['effect_log.request_id'] = result["request_id"]
        
        # Capture response
        response_data = []
        status_code = [None]
        
        def custom_start_response(status, headers, exc_info=None):
            status_code[0] = int(status.split()[0])
            response_data.extend([status, headers])
            return start_response(status, headers, exc_info)
        
        try:
            response = self.app(environ, custom_start_response)
            
            # Log response
            duration = time.time() - start_time
            mock_response = self._create_response(status_code[0])
            self.http_middleware._log_response(logger, mock_response, duration)
            
            return response
        except Exception as e:
            logger.error("WSGI application error", error=str(e))
            raise
    
    def _create_request(self, environ):
        """Create mock request object from WSGI environ"""
        class MockRequest:
            def __init__(self, environ):
                self.method = environ.get('REQUEST_METHOD', 'GET')
                self.path = environ.get('PATH_INFO', '/')
                self.query_string = environ.get('QUERY_STRING', '')
                self.headers = self._extract_headers(environ)
                self.remote_addr = environ.get('REMOTE_ADDR')
            
            def _extract_headers(self, environ):
                headers = {}
                for key, value in environ.items():
                    if key.startswith('HTTP_'):
                        header_name = key[5:].replace('_', '-').lower()
                        headers[header_name] = value
                return headers
        
        return MockRequest(environ)
    
    def _create_response(self, status_code):
        """Create mock response object"""
        class MockResponse:
            def __init__(self, status_code):
                self.status_code = status_code
        
        return MockResponse(status_code)
```

### Generic ASGI Integration

```python
from effect_log import Logger
from effect_log.middleware import HttpLoggerMiddleware
import time

class EffectLogASGIMiddleware:
    def __init__(self, app, logger=None):
        self.app = app
        self.logger = logger or Logger()
        self.http_middleware = HttpLoggerMiddleware(self.logger)
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Create mock request
        request = self._create_request(scope)
        
        # Process request
        result = self.http_middleware(request)
        logger = result["logger"]
        start_time = result["start_time"]
        
        # Store in scope
        scope["effect_log"] = {
            "logger": logger,
            "request_id": result["request_id"],
            "start_time": start_time
        }
        
        # Wrap send to capture response
        async def wrapped_send(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                duration = time.time() - start_time
                
                # Log response
                mock_response = self._create_response(status_code)
                self.http_middleware._log_response(logger, mock_response, duration)
            
            await send(message)
        
        try:
            await self.app(scope, receive, wrapped_send)
        except Exception as e:
            logger.error("ASGI application error", error=str(e))
            raise
    
    def _create_request(self, scope):
        """Create mock request from ASGI scope"""
        class MockRequest:
            def __init__(self, scope):
                self.method = scope["method"]
                self.path = scope["path"]
                self.query_string = scope.get("query_string", b"").decode()
                self.headers = dict(scope.get("headers", []))
                self.remote_addr = scope.get("client", [None])[0]
        
        return MockRequest(scope)
    
    def _create_response(self, status_code):
        """Create mock response object"""
        class MockResponse:
            def __init__(self, status_code):
                self.status_code = status_code
        
        return MockResponse(status_code)
```

## Best Practices for Framework Integration

### 1. Request ID Generation

```python
import uuid

def generate_request_id():
    return str(uuid.uuid4())

# Use in middleware
request_id = request.headers.get("X-Request-ID", generate_request_id())
```

### 2. Correlation ID Propagation

```python
# Extract correlation ID from headers
correlation_id = request.headers.get("X-Correlation-ID")
if correlation_id:
    logger = logger.with_context(correlation_id=correlation_id)
```

### 3. User Context

```python
# Add user context when available
if hasattr(request, 'user') and request.user.is_authenticated:
    logger = logger.with_context(
        user_id=request.user.id,
        user_email=request.user.email
    )
```

### 4. Error Propagation

```python
# Ensure errors are logged at framework level
try:
    response = await call_next(request)
except Exception as e:
    logger.error("Framework error", 
        error=str(e),
        error_type=type(e).__name__,
        traceback=traceback.format_exc()
    )
    raise
```

### 5. Performance Monitoring

```python
# Track request duration
start_time = time.time()
try:
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info("Request completed", duration_ms=duration * 1000)
except Exception as e:
    duration = time.time() - start_time
    logger.error("Request failed", 
        duration_ms=duration * 1000,
        error=str(e)
    )
    raise
```

This comprehensive integration guide should help you integrate effect-log with any Python web framework, providing structured logging with distributed tracing capabilities.