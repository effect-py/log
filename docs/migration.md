# Migration Guide

This guide helps you migrate from other logging libraries to effect-log.

## Table of Contents

- [From Python's Built-in Logging](#from-pythons-built-in-logging)
- [From Loguru](#from-loguru)
- [From Structlog](#from-structlog)
- [From Custom Logging Solutions](#from-custom-logging-solutions)
- [Common Migration Patterns](#common-migration-patterns)
- [Breaking Changes](#breaking-changes)
- [Migration Tools](#migration-tools)

## From Python's Built-in Logging

### Basic Logging

**Before (Python logging):**
```python
import logging

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Usage
logger.info("User logged in", extra={"user_id": "123"})
logger.error("Database error", exc_info=True)
```

**After (effect-log):**
```python
from effect_log import Logger

# Setup
logger = Logger()

# Usage
logger.info("User logged in", user_id="123")
logger.error("Database error", error=str(e))
```

### Advanced Configuration

**Before:**
```python
import logging
import logging.handlers

# Create logger
logger = logging.getLogger('myapp')
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# File handler
file_handler = logging.handlers.RotatingFileHandler(
    'app.log', maxBytes=10*1024*1024, backupCount=5
)
file_handler.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)
```

**After:**
```python
from effect_log import Logger
from effect_log.writers import MultiWriter, ConsoleWriter, FileWriter

logger = Logger(
    writer=MultiWriter(
        ConsoleWriter(min_level=LogLevel.INFO),
        FileWriter("app.log", min_level=LogLevel.DEBUG)
    )
)
```

### Structured Logging

**Before:**
```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
        }
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        return json.dumps(log_entry)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

# Usage
logger.info("User action", extra={"user_id": "123", "action": "login"})
```

**After:**
```python
from effect_log import Logger
from effect_log.writers import JSONConsoleWriter

logger = Logger(writer=JSONConsoleWriter())

# Usage
logger.info("User action", user_id="123", action="login")
```

### Context Managers

**Before:**
```python
import logging
from contextlib import contextmanager

@contextmanager
def log_context(**kwargs):
    # Add context to all log records
    old_factory = logging.getLogRecordFactory()
    
    def record_factory(*args, **factory_kwargs):
        record = old_factory(*args, **factory_kwargs)
        for key, value in kwargs.items():
            setattr(record, key, value)
        return record
    
    logging.setLogRecordFactory(record_factory)
    try:
        yield
    finally:
        logging.setLogRecordFactory(old_factory)

# Usage
with log_context(user_id="123", session_id="abc"):
    logger.info("User action")
```

**After:**
```python
from effect_log import Logger

logger = Logger()

# Usage
user_logger = logger.with_context(user_id="123", session_id="abc")
user_logger.info("User action")
```

## From Loguru

### Basic Setup

**Before (Loguru):**
```python
from loguru import logger

# Configuration
logger.add("app.log", rotation="10 MB", retention="1 week")
logger.add(sys.stdout, format="{time} | {level} | {message}")

# Usage
logger.info("User logged in", user_id="123")
logger.bind(request_id="abc123").info("Processing request")
```

**After (effect-log):**
```python
from effect_log import Logger
from effect_log.writers import MultiWriter, ConsoleWriter, FileWriter

logger = Logger(
    writer=MultiWriter(
        ConsoleWriter(),
        FileWriter("app.log")
    )
)

# Usage
logger.info("User logged in", user_id="123")
logger.with_context(request_id="abc123").info("Processing request")
```

### Structured Logging

**Before:**
```python
from loguru import logger

# Structured logging
logger.info("User action", user_id="123", action="login", ip="192.168.1.1")

# Binding context
logger_with_context = logger.bind(user_id="123", session_id="abc")
logger_with_context.info("User action")
```

**After:**
```python
from effect_log import Logger

logger = Logger()

# Structured logging
logger.info("User action", user_id="123", action="login", ip="192.168.1.1")

# Context binding
logger_with_context = logger.with_context(user_id="123", session_id="abc")
logger_with_context.info("User action")
```

### Custom Serialization

**Before:**
```python
from loguru import logger
import json

def serialize(record):
    subset = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
    }
    return json.dumps(subset)

logger.add("app.log", serialize=serialize)
```

**After:**
```python
from effect_log import Logger
from effect_log.writers import JSONConsoleWriter

logger = Logger(writer=JSONConsoleWriter())
```

## From Structlog

### Basic Configuration

**Before (Structlog):**
```python
import structlog

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
```

**After (effect-log):**
```python
from effect_log import Logger
from effect_log.writers import JSONConsoleWriter

logger = Logger(writer=JSONConsoleWriter())
```

### Context Binding

**Before:**
```python
import structlog

logger = structlog.get_logger()

# Bind context
logger_with_context = logger.bind(user_id="123", session_id="abc")
logger_with_context.info("User action", action="login")

# New context
logger_with_more_context = logger_with_context.bind(ip="192.168.1.1")
logger_with_more_context.info("Login attempt")
```

**After:**
```python
from effect_log import Logger

logger = Logger()

# Bind context
logger_with_context = logger.with_context(user_id="123", session_id="abc")
logger_with_context.info("User action", action="login")

# New context
logger_with_more_context = logger_with_context.with_context(ip="192.168.1.1")
logger_with_more_context.info("Login attempt")
```

### Processors

**Before:**
```python
import structlog

def add_request_id(logger, method_name, event_dict):
    event_dict["request_id"] = get_current_request_id()
    return event_dict

structlog.configure(
    processors=[
        add_request_id,
        structlog.processors.JSONRenderer()
    ]
)
```

**After:**
```python
from effect_log import Logger, with_context

def with_request_id(logger):
    return logger.with_context(request_id=get_current_request_id())

logger = Logger().pipe(with_request_id)
```

## From Custom Logging Solutions

### Dictionary-Based Logging

**Before:**
```python
import json
import sys
from datetime import datetime

class CustomLogger:
    def __init__(self, level="INFO"):
        self.level = level
    
    def log(self, level, message, **kwargs):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        print(json.dumps(entry), file=sys.stdout)
    
    def info(self, message, **kwargs):
        self.log("INFO", message, **kwargs)

logger = CustomLogger()
logger.info("User action", user_id="123")
```

**After:**
```python
from effect_log import Logger
from effect_log.writers import JSONConsoleWriter

logger = Logger(writer=JSONConsoleWriter())
logger.info("User action", user_id="123")
```

### Class-Based Context

**Before:**
```python
class ContextualLogger:
    def __init__(self, **context):
        self.context = context
    
    def with_context(self, **kwargs):
        new_context = {**self.context, **kwargs}
        return ContextualLogger(**new_context)
    
    def info(self, message, **kwargs):
        all_context = {**self.context, **kwargs}
        print(f"INFO: {message} - {all_context}")

logger = ContextualLogger(service="api")
user_logger = logger.with_context(user_id="123")
user_logger.info("User action")
```

**After:**
```python
from effect_log import Logger

logger = Logger().with_context(service="api")
user_logger = logger.with_context(user_id="123")
user_logger.info("User action")
```

## Common Migration Patterns

### 1. Gradual Migration

```python
# Phase 1: Add effect-log alongside existing logging
import logging
from effect_log import Logger

# Keep existing logging
old_logger = logging.getLogger(__name__)

# Add effect-log
new_logger = Logger()

def dual_log_info(message, **kwargs):
    """Log to both systems during migration."""
    old_logger.info(message, extra=kwargs)
    new_logger.info(message, **kwargs)

# Phase 2: Replace logging calls gradually
# dual_log_info("User action", user_id="123")

# Phase 3: Remove old logging system
# new_logger.info("User action", user_id="123")
```

### 2. Wrapper Pattern

```python
# Create wrapper to ease migration
class MigrationLogger:
    def __init__(self, effect_logger):
        self.logger = effect_logger
    
    def info(self, message, extra=None, **kwargs):
        """Compatible with both old and new style."""
        context = {}
        if extra:
            context.update(extra)
        context.update(kwargs)
        self.logger.info(message, **context)
    
    def bind(self, **kwargs):
        """Loguru/Structlog compatibility."""
        return MigrationLogger(self.logger.with_context(**kwargs))

# Usage
logger = MigrationLogger(Logger())
logger.info("User action", extra={"user_id": "123"})
logger.bind(user_id="123").info("User action")
```

### 3. Configuration Migration

```python
# Old configuration
OLD_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default"
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "default"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    }
}

# Convert to effect-log
def migrate_config(old_config):
    from effect_log import Logger, LogLevel
    from effect_log.writers import MultiWriter, ConsoleWriter, FileWriter
    
    writers = []
    
    # Convert handlers
    for handler_name, handler_config in old_config["handlers"].items():
        if handler_config["class"] == "logging.StreamHandler":
            writers.append(ConsoleWriter())
        elif handler_config["class"] == "logging.FileHandler":
            writers.append(FileWriter(handler_config["filename"]))
    
    # Convert level
    level_str = old_config["root"]["level"]
    level = LogLevel[level_str]
    
    # Create logger
    return Logger(
        writer=MultiWriter(*writers) if len(writers) > 1 else writers[0],
        min_level=level
    )

logger = migrate_config(OLD_CONFIG)
```

## Breaking Changes

### Version 0.1.0b1

#### Context API Changes
- **Old:** `logger.info("message", extra={"key": "value"})`
- **New:** `logger.info("message", key="value")`

#### Writer API Changes
- **Old:** Multiple writers passed as list
- **New:** Use `MultiWriter` for multiple outputs

#### Level Filtering
- **Old:** Filtering handled by handlers
- **New:** Filtering at logger and writer level

### Migration Helper

```python
def migrate_log_call(old_call_args):
    """Helper to migrate old-style log calls."""
    message = old_call_args.get("message", "")
    extra = old_call_args.get("extra", {})
    
    # Convert extra dict to kwargs
    kwargs = {}
    if extra:
        kwargs.update(extra)
    
    return message, kwargs

# Example usage
old_args = {"message": "User login", "extra": {"user_id": "123"}}
message, kwargs = migrate_log_call(old_args)
logger.info(message, **kwargs)
```

## Migration Tools

### Automatic Code Migration

```python
# migration_tool.py
import ast
import re

class LoggingMigrator(ast.NodeTransformer):
    """AST transformer to migrate logging calls."""
    
    def visit_Call(self, node):
        # Transform logging.getLogger() calls
        if (isinstance(node.func, ast.Attribute) and 
            isinstance(node.func.value, ast.Name) and
            node.func.value.id == 'logging' and
            node.func.attr == 'getLogger'):
            
            # Replace with Logger()
            return ast.Call(
                func=ast.Name(id='Logger', ctx=ast.Load()),
                args=[],
                keywords=[]
            )
        
        # Transform logger.info(msg, extra={...}) calls
        if (isinstance(node.func, ast.Attribute) and
            node.func.attr in ['info', 'debug', 'warning', 'error']):
            
            # Extract extra keyword argument
            new_keywords = []
            for keyword in node.keywords:
                if keyword.arg == 'extra':
                    # Convert extra dict to individual kwargs
                    if isinstance(keyword.value, ast.Dict):
                        for key, value in zip(keyword.value.keys, keyword.value.values):
                            if isinstance(key, ast.Str):
                                new_keywords.append(ast.keyword(arg=key.s, value=value))
                else:
                    new_keywords.append(keyword)
            
            return ast.Call(
                func=node.func,
                args=node.args,
                keywords=new_keywords
            )
        
        return self.generic_visit(node)

# Usage
def migrate_file(filename):
    with open(filename, 'r') as f:
        code = f.read()
    
    tree = ast.parse(code)
    migrator = LoggingMigrator()
    new_tree = migrator.visit(tree)
    
    new_code = ast.unparse(new_tree)
    
    with open(filename + '.migrated', 'w') as f:
        f.write(new_code)
```

### Configuration Converter

```python
# config_converter.py
import yaml
import json

def convert_logging_config(old_config_file, new_config_file):
    """Convert old logging config to effect-log config."""
    
    with open(old_config_file, 'r') as f:
        if old_config_file.endswith('.yaml'):
            old_config = yaml.safe_load(f)
        else:
            old_config = json.load(f)
    
    # Convert to effect-log config
    new_config = {
        "service": "migrated-service",
        "version": "1.0.0",
        "log_level": old_config.get("root", {}).get("level", "INFO"),
        "writers": []
    }
    
    # Convert handlers
    for handler_name, handler_config in old_config.get("handlers", {}).items():
        if handler_config.get("class") == "logging.StreamHandler":
            new_config["writers"].append({
                "type": "console",
                "use_colors": True
            })
        elif handler_config.get("class") == "logging.FileHandler":
            new_config["writers"].append({
                "type": "file",
                "path": handler_config.get("filename", "app.log")
            })
    
    with open(new_config_file, 'w') as f:
        json.dump(new_config, f, indent=2)

# Usage
convert_logging_config("old_logging.yaml", "effect_log_config.json")
```

### Testing Migration

```python
# test_migration.py
import unittest
from unittest.mock import patch, Mock

class TestMigration(unittest.TestCase):
    def setUp(self):
        self.mock_writer = Mock()
        self.logger = Logger(writer=self.mock_writer)
    
    def test_basic_migration(self):
        """Test basic log call migration."""
        # Old style (simulated)
        message = "User login"
        extra = {"user_id": "123", "ip": "192.168.1.1"}
        
        # New style
        self.logger.info(message, **extra)
        
        # Verify
        self.mock_writer.write.assert_called_once()
        entry = self.mock_writer.write.call_args[0][0]
        self.assertEqual(entry.message, message)
        self.assertEqual(entry.context["user_id"], "123")
        self.assertEqual(entry.context["ip"], "192.168.1.1")
    
    def test_context_migration(self):
        """Test context binding migration."""
        # Old style: logger.bind(user_id="123")
        # New style: logger.with_context(user_id="123")
        
        user_logger = self.logger.with_context(user_id="123")
        user_logger.info("User action")
        
        entry = self.mock_writer.write.call_args[0][0]
        self.assertEqual(entry.context["user_id"], "123")

if __name__ == '__main__':
    unittest.main()
```

This migration guide should help you transition from any logging library to effect-log with minimal disruption to your existing codebase.