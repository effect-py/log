---
name: Performance Issue
about: Report a performance problem with effect-log
title: "[PERFORMANCE] "
labels: ["performance", "needs-triage"]
assignees: []
---

## Performance Issue Summary
<!-- Brief description of the performance problem -->

## Performance Impact
<!-- How does this performance issue affect your application? -->
- [ ] High CPU usage
- [ ] High memory usage
- [ ] Slow response times
- [ ] High I/O operations
- [ ] Blocking operations
- [ ] Other: _____

## Measurements
<!-- Provide specific measurements if available -->

### Current Performance
- **Metric**: [e.g., requests per second, memory usage, CPU usage]
- **Measured Value**: [e.g., 100 req/s, 500MB RAM, 80% CPU]
- **Measurement Tool**: [e.g., pytest-benchmark, memory_profiler, cProfile]

### Expected Performance
- **Expected Value**: [e.g., 1000 req/s, 50MB RAM, 20% CPU]
- **Reasoning**: [Why do you expect this performance level?]

## Reproduction
<!-- Steps to reproduce the performance issue -->

### Environment
- **effect-log version**: [e.g., 0.1.0b1]
- **Python version**: [e.g., 3.11.0]
- **Operating System**: [e.g., Ubuntu 22.04]
- **Hardware**: [e.g., 4 CPU cores, 8GB RAM]
- **Load**: [e.g., 1000 concurrent users, 10,000 log entries/second]

### Code Example
<!-- Provide a minimal code example that demonstrates the performance issue -->

```python
from effect_log import Logger
import time

# Your performance test code here
logger = Logger()

# Example performance test
start_time = time.time()
for i in range(10000):
    logger.info(f"Log entry {i}", user_id=f"user_{i}")
end_time = time.time()

print(f"Time taken: {end_time - start_time:.2f} seconds")
```

### Benchmark Results
<!-- If you've run benchmarks, include the results -->

```
Paste benchmark results here
```

## Profiling Data
<!-- If you've profiled the code, include relevant data -->

<details>
<summary>Profiling Output</summary>

```
Paste profiling output here (cProfile, memory_profiler, etc.)
```

</details>

## Configuration
<!-- What configuration are you using? -->

### Logger Configuration
```python
# Your logger configuration
logger = Logger(
    writer=...,
    min_level=...,
    # other configuration
)
```

### Writer Configuration
```python
# Your writer configuration
writer = SomeWriter(
    # configuration options
)
```

## Comparison
<!-- Have you compared with other logging libraries? -->
- [ ] No comparison done
- [ ] Compared with Python's built-in logging
- [ ] Compared with other logging libraries
- [ ] Compared with previous effect-log versions

### Comparison Results
<!-- If you've done comparisons, share the results -->

| Library | Performance Metric | Value |
|---------|-------------------|-------|
| effect-log | | |
| logging | | |
| other | | |

## Suspected Cause
<!-- If you have suspicions about what might be causing the performance issue -->
- [ ] Excessive object creation
- [ ] Inefficient string formatting
- [ ] Blocking I/O operations
- [ ] Memory leaks
- [ ] Inefficient algorithms
- [ ] Missing caching/optimization
- [ ] Other: _____

## Proposed Solution
<!-- If you have ideas for how to fix the performance issue -->

## Impact Assessment
<!-- How critical is this performance issue? -->
- [ ] Critical - Application is unusable
- [ ] High - Significantly impacts user experience
- [ ] Medium - Noticeable but manageable
- [ ] Low - Minor performance concern

## Scale Information
<!-- Information about the scale at which you're using effect-log -->
- **Log volume**: [e.g., 1000 logs/second, 1M logs/day]
- **Concurrent users**: [e.g., 100 concurrent users]
- **Application type**: [e.g., web API, batch processing, real-time system]
- **Deployment**: [e.g., single server, distributed system, cloud]

## Workaround
<!-- If you've found a workaround, please describe it -->

## Additional Context
<!-- Any other context about the performance issue -->

## Checklist
<!-- Please check the boxes that apply -->
- [ ] I have provided specific performance measurements
- [ ] I have included a reproducible code example
- [ ] I have profiled the code (if possible)
- [ ] I have tested with the latest version of effect-log
- [ ] I have compared with other logging solutions (if relevant)
- [ ] I have considered the scale and load of my use case
- [ ] I am willing to help test potential fixes

## Related Issues
<!-- Link any related performance issues -->
- Related to #
- Duplicate of #
- Blocks #

---

**Note**: For general questions about optimizing performance, please use the question template instead.