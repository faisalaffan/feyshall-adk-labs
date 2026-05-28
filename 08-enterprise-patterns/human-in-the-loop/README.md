---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Human-in-the-Loop

## Concept

Before an agent takes a high-stakes action (delete data, send money, email a customer), a human must approve. This pattern is required for compliance in finance, healthcare, and enterprise workflows.

## Approval Flow

```
User Request → Agent processes → Agent proposes action
                                      │
                                      ▼
                               Human reviews
                              │           │
                          Approve       Reject
                              │           │
                              ▼           ▼
                        Execute      Return reason
```

## Code

```python
from enum import Enum
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

# Store pending approvals (Redis in production)
pending_approvals = {}

def request_approval(action: str, details: dict) -> str:
    """Request human approval for a high-stakes action.

    Args:
        action: The action being proposed (e.g., 'send_email', 'delete_record').
        details: Context the approver needs to make a decision.
    """
    approval_id = f"approval-{len(pending_approvals) + 1}"
    pending_approvals[approval_id] = {
        "action": action,
        "details": details,
        "status": ApprovalStatus.PENDING,
    }
    return f"Approval requested: {approval_id}. Awaiting human review."

def check_approval(approval_id: str) -> str:
    """Check the status of a pending approval.

    Args:
        approval_id: The approval ID returned by request_approval.
    """
    approval = pending_approvals.get(approval_id)
    if not approval:
        return "Approval not found."
    return f"Status: {approval['status'].value}"

# Agent that knows when to ask for approval
agent = Agent(
    name="hr-agent",
    model="gemini-2.5-flash",
    tools=[
        FunctionTool(request_approval),
        FunctionTool(check_approval),
    ],
    instruction="""You are an HR assistant. For routine queries, respond directly.
    For high-stakes actions (sending emails to all staff, modifying payroll data,
    deleting records), use request_approval first and wait for approval before
    executing.""",
)
```

## Production-Grade Approval

```python
# Use a database + notification system in production
class ApprovalWorkflow:
    def __init__(self, db, notifier):
        self.db = db
        self.notifier = notifier  # Slack, email, PagerDuty

    def create_approval(self, action, details, requested_by):
        approval = self.db.create({
            "action": action,
            "details": details,
            "requested_by": requested_by,
            "status": "pending",
            "created_at": now(),
        })
        self.notifier.send(
            channel="#agent-approvals",
            message=f"New approval needed: {action} by {requested_by}",
            actions=["Approve", "Reject"],
        )
        return approval.id

    def resolve(self, approval_id, decision, resolved_by):
        self.db.update(approval_id, {
            "status": decision,
            "resolved_by": resolved_by,
            "resolved_at": now(),
        })
```

## When to Require Approval

| Action | Risk | Approval Required |
|--------|------|-------------------|
| Read data | Low | No |
| Generate report | Low | No |
| Send individual email | Medium | Optional |
| Send bulk email | High | Yes |
| Modify user data | High | Yes |
| Delete records | Critical | Yes + second approver |
| Financial transaction | Critical | Yes + second approver |

## Pitfalls

- **Approval timeout**: What happens if nobody approves for 24 hours? Auto-reject with expiry.
- **Approval fatigue**: If every action requires approval, humans start clicking "Approve" without reading. Reserve approvals for high-stakes actions only.
- **No approval bypass in code**: Don't build a "force execute" flag. It will be abused.
- **Async approval breaks the agent loop**: The agent must wait for approval in a separate turn. Design the conversation flow around this — the user may need to come back later.
