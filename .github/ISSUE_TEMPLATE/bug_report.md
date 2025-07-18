---
name: Bug Report
about: Create a report to help us improve effect-log
title: "[BUG] "
labels: ["bug", "needs-triage"]
assignees: []
---

## Bug Description
<!-- A clear and concise description of what the bug is -->

## Expected Behavior
<!-- A clear and concise description of what you expected to happen -->

## Actual Behavior
<!-- A clear and concise description of what actually happened -->

## Steps to Reproduce
<!-- Steps to reproduce the behavior -->
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Code Example
<!-- Please provide a minimal code example that reproduces the issue -->

```python
from effect_log import Logger

# Your code here that reproduces the bug
logger = Logger()
# ...
```

## Environment
<!-- Please complete the following information -->
- **effect-log version**: [e.g., 0.1.0b1]
- **Python version**: [e.g., 3.11.0]
- **Operating System**: [e.g., Ubuntu 22.04, macOS 13.0, Windows 11]
- **Framework** (if applicable): [e.g., Flask 2.3.0, FastAPI 0.104.0]

### Python Environment Details
<details>
<summary>Click to expand</summary>

```bash
# Run these commands and paste the output
python --version
pip show effect-log
pip freeze | grep -E "(flask|fastapi|django|starlette)"
```

</details>

## Error Messages and Stack Traces
<!-- If applicable, add the full error message and stack trace -->

```
Paste the full error message and stack trace here
```

## Log Output
<!-- If applicable, include relevant log output -->

```
Paste relevant log output here
```

## Screenshots
<!-- If applicable, add screenshots to help explain your problem -->

## Impact
<!-- How does this bug affect your use of effect-log? -->
- [ ] Blocks core functionality
- [ ] Causes incorrect behavior
- [ ] Performance impact
- [ ] Minor inconvenience
- [ ] Other: _____

## Workaround
<!-- If you found a workaround, please describe it here -->

## Additional Context
<!-- Add any other context about the problem here -->

## Checklist
<!-- Please check the boxes that apply -->
- [ ] I have searched for existing issues that describe the same problem
- [ ] I have tested with the latest version of effect-log
- [ ] I have provided a minimal code example that reproduces the issue
- [ ] I have included the complete error message and stack trace
- [ ] I have checked the documentation for relevant information
- [ ] I am willing to submit a pull request to fix this issue

## Related Issues
<!-- Link any related issues here -->
- Related to #
- Duplicate of #
- Blocks #

---

**Note**: For security vulnerabilities, please use the security template instead of this bug report template.