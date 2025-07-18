# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with effect-log.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Import Problems](#import-problems)
- [Configuration Issues](#configuration-issues)
- [Performance Problems](#performance-problems)
- [Output Issues](#output-issues)
- [Integration Problems](#integration-problems)
- [Memory Issues](#memory-issues)
- [Debugging Tips](#debugging-tips)

## Installation Issues

### Problem: pip install fails

**Symptoms:**
```bash
pip install effect-log
ERROR: Could not find a version that satisfies the requirement effect-log
```

**Solutions:**
1. Check Python version compatibility:
   ```bash
   python --version  # Must be 3.8+
   ```

2. Update pip:
   ```bash
   pip install --upgrade pip
   ```

3. Try installing from specific index:
   ```bash
   pip install --index-url https://pypi.org/simple/ effect-log
   ```

4. Install from source:
   ```bash
   pip install git+https://github.com/effect-py/log.git
   ```

### Problem: ImportError after installation

**Symptoms:**
```python
ImportError: No module named 'effect_log'
```

**Solutions:**
1. Check if installed in correct environment:
   ```bash
   pip list | grep effect-log
   ```

2. Verify import path:
   ```python
   # Correct
   from effect_log import Logger
   
   # Incorrect
   from effect-log import Logger  # Hyphen instead of underscore
   ```

3. Check virtual environment:
   ```bash
   which python
   which pip
   ```

## Import Problems

### Problem: Circular import errors

**Symptoms:**
```python
ImportError: cannot import name 'Logger' from partially initialized module 'effect_log'
```

**Solutions:**
1. Avoid importing at module level in modules that are imported by effect-log
2. Use lazy imports:
   ```python
   def get_logger():
       from effect_log import Logger
       return Logger()
   ```

3. Restructure imports to avoid circular dependencies

### Problem: Missing optional dependencies

**Symptoms:**
```python
ImportError: No module named 'flask'
```

**Solutions:**
1. Install web framework dependencies:
   ```bash
   pip install effect-log[web]
   ```

2. Or install specific frameworks:
   ```bash
   pip install flask fastapi django
   ```

## Configuration Issues

### Problem: Logger not outputting anything

**Symptoms:**
```python
logger = Logger()
logger.info("Test message")
# No output visible
```

**Solutions:**
1. Check log level:
   ```python
   from effect_log import Logger, LogLevel
   
   # Ensure logger level allows INFO
   logger = Logger(min_level=LogLevel.DEBUG)
   logger.info("Test message")
   ```

2. Check writer configuration:
   ```python
   from effect_log.writers import ConsoleWriter
   
   # Ensure writer level allows INFO
   writer = ConsoleWriter(min_level=LogLevel.INFO)
   logger = Logger(writer=writer)
   ```

3. Verify output stream:
   ```python
   import sys
   from effect_log.writers import ConsoleWriter
   
   # Explicitly set stdout
   writer = ConsoleWriter(stream=sys.stdout)
   logger = Logger(writer=writer)
   ```

### Problem: File logging not working

**Symptoms:**
```python
logger = Logger(writer=FileWriter("app.log"))
logger.info("Test message")
# No file created
```

**Solutions:**
1. Check file permissions:
   ```python
   import os
   from pathlib import Path
   
   log_file = Path("app.log")
   print(f"Parent directory exists: {log_file.parent.exists()}")
   print(f"Parent directory writable: {os.access(log_file.parent, os.W_OK)}")
   ```

2. Use absolute path:
   ```python
   from pathlib import Path
   
   log_file = Path.cwd() / "app.log"
   logger = Logger(writer=FileWriter(log_file))
   ```

3. Check directory creation:
   ```python
   from pathlib import Path
   from effect_log.writers import FileWriter
   
   log_dir = Path("logs")
   log_dir.mkdir(exist_ok=True)
   logger = Logger(writer=FileWriter(log_dir / "app.log"))
   ```

### Problem: JSON output malformed

**Symptoms:**
```python
logger = Logger(writer=JSONConsoleWriter())
logger.info("Test", data={"key": "value"})
# Output: {"timestamp": "...", "level": "INFO", "message": "Test", "context": {"data": "{'key': 'value'}"}}
```

**Solutions:**
1. Ensure JSON-serializable data:
   ```python
   # Good
   logger.info("Test", data={"key": "value"})
   
   # Bad - objects not JSON serializable
   logger.info("Test", data=some_object)
   ```

2. Use proper data types:
   ```python
   from datetime import datetime
   
   # Convert non-serializable objects
   logger.info("Test", timestamp=datetime.now().isoformat())
   ```

## Performance Problems

### Problem: Slow logging performance

**Symptoms:**
- Application becomes slow when logging is enabled
- High CPU usage during logging operations

**Solutions:**
1. Use buffered writing:
   ```python
   from effect_log.writers import BufferedWriter, FileWriter
   
   buffered_writer = BufferedWriter(
       FileWriter("app.log"),
       buffer_size=1000  # Increase buffer size
   )
   logger = Logger(writer=buffered_writer)
   ```

2. Optimize log level filtering:
   ```python
   # Set appropriate minimum levels
   logger = Logger(min_level=LogLevel.INFO)  # Skip DEBUG/TRACE
   ```

3. Use conditional logging:
   ```python
   if logger.min_level <= LogLevel.DEBUG:
       expensive_data = calculate_expensive_data()
       logger.debug("Debug info", data=expensive_data)
   ```

4. Avoid expensive operations in log calls:
   ```python
   # Bad
   logger.info("User data", user=user.to_dict())  # Expensive serialization
   
   # Good
   logger.info("User data", user_id=user.id, user_name=user.name)
   ```

### Problem: Memory usage grows over time

**Symptoms:**
- Application memory usage increases continuously
- Out of memory errors in long-running applications

**Solutions:**
1. Flush buffered writers:
   ```python
   import atexit
   
   buffered_writer = BufferedWriter(FileWriter("app.log"))
   atexit.register(buffered_writer.flush)
   ```

2. Limit context size:
   ```python
   # Avoid accumulating large contexts
   base_logger = Logger()
   
   # Create new loggers instead of chaining
   request_logger = base_logger.with_context(request_id="123")
   # Don't keep adding to the same logger
   ```

3. Use log rotation:
   ```python
   # Implement log rotation to prevent large files
   class RotatingFileWriter:
       def __init__(self, base_path, max_size_mb=10):
           self.base_path = Path(base_path)
           self.max_size_mb = max_size_mb
           
       def write(self, entry):
           if self.base_path.stat().st_size > self.max_size_mb * 1024 * 1024:
               # Rotate log file
               rotated_path = self.base_path.with_suffix(f".{time.time()}.log")
               self.base_path.rename(rotated_path)
           
           with open(self.base_path, "a") as f:
               f.write(entry.to_json() + "\n")
   ```

## Output Issues

### Problem: Colors not showing in console

**Symptoms:**
```python
logger = Logger(writer=ConsoleWriter(use_colors=True))
logger.error("Error message")
# No colors in output
```

**Solutions:**
1. Check terminal support:
   ```bash
   echo $TERM
   # Should show color-capable terminal like xterm-256color
   ```

2. Force color output:
   ```python
   import sys
   from effect_log.writers import ConsoleWriter
   
   # Force colors even if not detected
   writer = ConsoleWriter(use_colors=True)
   logger = Logger(writer=writer)
   ```

3. Test color support:
   ```python
   import sys
   
   print(f"stdout isatty: {sys.stdout.isatty()}")
   print(f"stderr isatty: {sys.stderr.isatty()}")
   ```

### Problem: Timestamps in wrong timezone

**Symptoms:**
```python
logger.info("Test message")
# Timestamp shows wrong timezone
```

**Solutions:**
1. Use UTC timestamps:
   ```python
   from datetime import datetime, timezone
   
   # Override timestamp in custom writer
   class UTCWriter:
       def __init__(self, writer):
           self.writer = writer
           
       def write(self, entry):
           # Convert to UTC
           utc_entry = LogEntry(
               timestamp=datetime.now(timezone.utc),
               level=entry.level,
               message=entry.message,
               context=entry.context,
               span_id=entry.span_id,
               trace_id=entry.trace_id
           )
           self.writer.write(utc_entry)
   ```

2. Format timestamps in output:
   ```python
   from effect_log.writers import ConsoleWriter
   
   class CustomConsoleWriter(ConsoleWriter):
       def _format_entry(self, entry):
           # Custom timestamp format
           timestamp = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S %Z")
           return f"[{timestamp}] {entry.level.name} {entry.message}"
   ```

## Integration Problems

### Problem: Flask middleware not working

**Symptoms:**
```python
# Logger not available in Flask routes
@app.route("/")
def index():
    g.logger.info("Test")  # AttributeError: 'g' object has no attribute 'logger'
```

**Solutions:**
1. Check middleware order:
   ```python
   @app.before_request
   def before_request():
       # This must run before route handlers
       result = middleware(request)
       g.logger = result["logger"]
   ```

2. Verify middleware is called:
   ```python
   @app.before_request
   def before_request():
       print("Before request called")  # Debug
       result = middleware(request)
       g.logger = result["logger"]
   ```

3. Check excluded paths:
   ```python
   middleware = HttpLoggerMiddleware(
       logger,
       exclude_paths=["/health"]  # Make sure your route isn't excluded
   )
   ```

### Problem: FastAPI middleware not working

**Symptoms:**
```python
# Logger not available in FastAPI routes
@app.get("/")
async def index(request: Request):
    request.state.logger.info("Test")  # AttributeError
```

**Solutions:**
1. Check middleware installation:
   ```python
   # Make sure middleware is added to app
   app.add_middleware(FastAPIMiddleware, middleware=http_middleware)
   ```

2. Verify middleware execution:
   ```python
   @app.middleware("http")
   async def logging_middleware(request: Request, call_next):
       print("Middleware called")  # Debug
       result = http_middleware(request)
       request.state.logger = result["logger"]
       response = await call_next(request)
       return response
   ```

### Problem: Django middleware not working

**Symptoms:**
```python
# Logger not available in Django views
def my_view(request):
    request.logger.info("Test")  # AttributeError
```

**Solutions:**
1. Check middleware in settings:
   ```python
   # settings.py
   MIDDLEWARE = [
       'effect_log.middleware.DjangoMiddleware',  # Must be present
       # ... other middleware
   ]
   ```

2. Verify middleware order:
   ```python
   # Put effect-log middleware early in the list
   MIDDLEWARE = [
       'effect_log.middleware.DjangoMiddleware',
       'django.middleware.security.SecurityMiddleware',
       # ... other middleware
   ]
   ```

## Memory Issues

### Problem: Memory leaks in long-running applications

**Symptoms:**
- Memory usage grows over time
- Application becomes slow or crashes

**Solutions:**
1. Use weak references for context:
   ```python
   import weakref
   
   # Avoid keeping references to large objects
   logger.info("Processing item", item_id=item.id)  # Not the full object
   ```

2. Clear context regularly:
   ```python
   # Create new loggers instead of chaining contexts
   def process_request(request_id):
       request_logger = base_logger.with_context(request_id=request_id)
       # Use request_logger for this request only
       # Don't keep adding context to the same logger
   ```

3. Monitor memory usage:
   ```python
   import psutil
   import os
   
   def log_memory_usage():
       process = psutil.Process(os.getpid())
       memory_mb = process.memory_info().rss / 1024 / 1024
       logger.info("Memory usage", memory_mb=memory_mb)
   ```

### Problem: Large log files consuming disk space

**Symptoms:**
- Disk space fills up quickly
- Application can't write logs due to disk space

**Solutions:**
1. Implement log rotation:
   ```python
   import shutil
   from pathlib import Path
   
   class RotatingFileWriter:
       def __init__(self, base_path, max_size_mb=100, backup_count=5):
           self.base_path = Path(base_path)
           self.max_size_mb = max_size_mb
           self.backup_count = backup_count
           
       def write(self, entry):
           if self._should_rotate():
               self._rotate_logs()
           
           with open(self.base_path, "a") as f:
               f.write(entry.to_json() + "\n")
   ```

2. Use log compression:
   ```python
   import gzip
   
   def compress_old_logs():
       for log_file in Path("logs").glob("*.log.1"):
           with open(log_file, 'rb') as f_in:
               with gzip.open(f"{log_file}.gz", 'wb') as f_out:
                   shutil.copyfileobj(f_in, f_out)
           log_file.unlink()
   ```

## Debugging Tips

### Enable Debug Mode

```python
# Enable debug logging for effect-log itself
import os
os.environ["EFFECT_LOG_DEBUG"] = "1"

from effect_log import Logger
logger = Logger()
```

### Use Test Writer

```python
# Test writer to capture logs for debugging
class TestWriter:
    def __init__(self):
        self.entries = []
    
    def write(self, entry):
        self.entries.append(entry)
        print(f"DEBUG: {entry.level.name} - {entry.message} - {entry.context}")

test_writer = TestWriter()
logger = Logger(writer=test_writer)
```

### Check Configuration

```python
# Debug logger configuration
def debug_logger_config(logger):
    print(f"Logger writer: {type(logger.writer)}")
    print(f"Logger min_level: {logger.min_level}")
    print(f"Logger context: {logger.context.data}")
    print(f"Logger span_id: {logger.context.span_id}")
    print(f"Logger trace_id: {logger.context.trace_id}")

debug_logger_config(logger)
```

### Verify File Operations

```python
# Debug file writing
import os
from pathlib import Path

def debug_file_writer(file_path):
    path = Path(file_path)
    print(f"File path: {path.absolute()}")
    print(f"Directory exists: {path.parent.exists()}")
    print(f"Directory writable: {os.access(path.parent, os.W_OK)}")
    print(f"File exists: {path.exists()}")
    if path.exists():
        print(f"File size: {path.stat().st_size}")
        print(f"File writable: {os.access(path, os.W_OK)}")

debug_file_writer("app.log")
```

### Profile Performance

```python
import cProfile
import pstats

def profile_logging():
    logger = Logger()
    
    def log_many():
        for i in range(1000):
            logger.info(f"Message {i}", iteration=i)
    
    cProfile.run('log_many()', 'logging_profile.prof')
    
    stats = pstats.Stats('logging_profile.prof')
    stats.sort_stats('cumulative')
    stats.print_stats(10)

profile_logging()
```

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `AttributeError: 'Logger' object has no attribute 'X'` | Typo in method name | Check API documentation |
| `TypeError: Object of type 'X' is not JSON serializable` | Non-serializable data in context | Convert to string or use serializable types |
| `FileNotFoundError: [Errno 2] No such file or directory` | Invalid file path | Check path exists and is writable |
| `PermissionError: [Errno 13] Permission denied` | Insufficient permissions | Check file/directory permissions |
| `RecursionError: maximum recursion depth exceeded` | Circular reference in context | Avoid circular references in logged data |

### Getting Help

If you're still having issues:

1. **Check the FAQ**: Common questions and answers
2. **Search existing issues**: [GitHub Issues](https://github.com/effect-py/log/issues)
3. **Create a minimal reproduction**: Isolate the problem
4. **Check versions**: Ensure you're using compatible versions
5. **Enable debug logging**: Use debug mode to get more information
6. **Ask for help**: Create a new issue with full details

### Minimal Reproduction Template

```python
"""
Minimal reproduction of the issue.
Please replace this with your actual problematic code.
"""

from effect_log import Logger

# Minimal code that reproduces the issue
logger = Logger()
logger.info("This should work but doesn't")

# Expected behavior: [describe what should happen]
# Actual behavior: [describe what actually happens]
# Error message: [paste full error if any]

# Environment information:
# - effect-log version: [run: pip show effect-log]
# - Python version: [run: python --version]
# - Operating system: [e.g., Ubuntu 22.04, macOS 13.0, Windows 11]
```