---
adk_version: "1.28"
level: advanced
languages: [python]
---

# RBAC for Agents

## Concept

Not every user should trigger every agent. Role-Based Access Control (RBAC) ensures that only authorized users can invoke specific agents, tools, or actions.

## Agent-Level RBAC

```python
from enum import Enum
from functools import wraps

class Role(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"

AGENT_PERMISSIONS = {
    "delete-data-agent": {Role.ADMIN},
    "financial-report-agent": {Role.ADMIN, Role.MANAGER},
    "customer-support-agent": {Role.ADMIN, Role.MANAGER, Role.ANALYST},
    "faq-agent": {Role.ADMIN, Role.MANAGER, Role.ANALYST, Role.VIEWER},
}

def require_role(allowed_roles: set[Role]):
    """Decorator to enforce RBAC on agent invocation."""

    def decorator(func):
        @wraps(func)
        def wrapper(user, *args, **kwargs):
            user_role = get_user_role(user)
            if user_role not in allowed_roles:
                raise PermissionError(
                    f"User role '{user_role.value}' cannot access "
                    f"'{func.__name__}'. Required: {[r.value for r in allowed_roles]}"
                )
            return func(user, *args, **kwargs)
        return wrapper
    return decorator

@require_role({Role.ADMIN})
def run_delete_agent(user, input_text):
    return run_agent(delete_agent, input_text)
```

## Tool-Level RBAC

```python
class RBACTool:
    """Tool that checks permissions before execution."""

    def __init__(self, tool_func, required_role: Role):
        self.tool_func = tool_func
        self.required_role = required_role

    def __call__(self, user, *args, **kwargs):
        if get_user_role(user) != self.required_role:
            return {
                "error": "Insufficient permissions",
                "required_role": self.required_role.value,
            }
        return self.tool_func(*args, **kwargs)
```

## RBAC Decision Flow

```
User request → Authenticate → Resolve roles → Check agent permissions
                                                   │
                                    ┌──────────────┼──────────────┐
                                    ▼              ▼              ▼
                                Allowed        Denied          Not found
                                    │              │              │
                                    ▼              ▼              ▼
                              Run agent      Return 403     Return 404
                                            (hide existence)
```

## Pitfalls

- **Return 404 on unauthorized**: Don't reveal that an agent exists if the user can't access it. This prevents enumeration attacks.
- **Tool permissions ≠ agent permissions**: A user might have access to the agent but not all its tools. Check at tool invocation time.
- **Hardcoded roles in code**: Roles change. Store RBAC mappings in a database or config file, not in Python enums.
- **No audit of access denials**: Log every 403. A spike in denials for a specific agent or user is a security signal.
