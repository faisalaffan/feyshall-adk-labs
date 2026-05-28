---
adk_version: "1.28"
level: advanced
languages: [python]
---

# ERP Workflow Automation

## Concept

Automate enterprise approval chains with agents: purchase requests flow through manager → finance → procurement, with each step handled by a specialized agent.

## Architecture

```
Employee: "Need 10 laptops for new hires"
    │
    ▼
Intake Agent (collects: quantity, model, budget, justification)
    │
    ▼
Manager Agent (approves/rejects based on budget authority)
    │
    ▼
Finance Agent (verifies budget, suggests cheaper alternatives)
    │
    ▼
Procurement Agent (checks stock, creates PO, estimates delivery)
    │
    ▼
Notification Agent (emails all parties with status)
```

## Code Skeleton

```python
from enum import Enum
from dataclasses import dataclass

class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_INFO = "needs_info"

@dataclass
class PurchaseRequest:
    requester: str
    item: str
    quantity: int
    budget_per_unit: float
    justification: str
    manager_approval: ApprovalStatus = ApprovalStatus.PENDING
    finance_approval: ApprovalStatus = ApprovalStatus.PENDING
    procurement_status: str = ""

intake_agent = Agent(
    name="intake",
    model="gemini-2.5-flash",
    instruction="""Collect purchase request details:
    - What item and quantity?
    - Budget per unit?
    - Business justification?
    If any field is missing, ask for it. Don't proceed until complete.""",
)

manager_agent = Agent(
    name="manager",
    model="gemini-2.5-flash",
    instruction="""Review purchase requests:
    - Under $1,000: auto-approve
    - $1,000-$10,000: approve if justification is clear
    - Over $10,000: flag for VP review
    Always explain your decision.""",
    tools=[FunctionTool(check_department_budget)],
)

finance_agent = Agent(
    name="finance",
    model="gemini-2.5-flash",
    instruction="""Verify budget availability. If budget is insufficient:
    1. Suggest cheaper alternatives
    2. Propose partial approval (fewer units)
    3. Flag for next quarter budget if urgent""",
    tools=[FunctionTool(check_budget), FunctionTool(find_cheaper_alternatives)],
)

procurement_agent = Agent(
    name="procurement",
    model="gemini-2.5-flash",
    instruction="""Check inventory and supplier availability:
    - In stock? Reserve immediately
    - Out of stock? Create purchase order, estimate delivery
    Return PO number and ETA.""",
    tools=[FunctionTool(check_inventory), FunctionTool(create_purchase_order)],
)
```

## Workflow Engine

```python
class ERPWorkflow:
    def __init__(self):
        self.steps = [
            ("intake", intake_agent),
            ("manager", manager_agent),
            ("finance", finance_agent),
            ("procurement", procurement_agent),
        ]

    async def process(self, user_input: str) -> dict:
        result = {"request": user_input, "steps": {}}

        for step_name, agent in self.steps:
            step_result = await run_agent_async(agent, user_input)
            result["steps"][step_name] = {
                "status": extract_status(step_result),
                "output": step_result,
            }
            if extract_status(step_result) == ApprovalStatus.REJECTED:
                result["outcome"] = f"Rejected at {step_name}"
                return result

        result["outcome"] = "Approved — purchase order created"
        return result
```

## Pitfalls

- **Approval chain length**: 4 steps × 2s per step = 8s minimum. For urgent requests, this feels slow. Allow parallel where possible.
- **Idempotency**: If the workflow crashes after creating a PO, restarting creates a duplicate. Use idempotency keys.
- **Hard-coded thresholds**: $1,000 approval limit changes with inflation and policy. Store thresholds in config, not prompts.
