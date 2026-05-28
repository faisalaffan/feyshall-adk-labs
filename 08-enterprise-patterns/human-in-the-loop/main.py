"""Human-in-the-Loop — runnable approval workflow example.
Run: python 08-enterprise-patterns/human-in-the-loop/main.py
"""
import os
from enum import Enum
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# In-memory approval store (Redis in production)
pending_approvals: dict = {}


def request_approval(action: str, details: str) -> str:
    """Request human approval for a high-stakes action.

    Args:
        action: The action being proposed (e.g., 'send_bulk_email').
        details: What the approver needs to know.
    """
    approval_id = f"APR-{len(pending_approvals) + 1:04d}"
    pending_approvals[approval_id] = {
        "action": action,
        "details": details,
        "status": ApprovalStatus.PENDING,
    }
    return (
        f"Approval requested: {approval_id}\n"
        f"Action: {action}\n"
        f"Details: {details}\n"
        f"Status: PENDING — awaiting human review."
    )


def check_approval(approval_id: str) -> str:
    """Check status of a pending approval.

    Args:
        approval_id: The approval ID from request_approval.
    """
    approval = pending_approvals.get(approval_id)
    if not approval:
        return f"Approval {approval_id} not found."
    return f"Approval {approval_id}: {approval['status'].value} — {approval['details']}"


def simulate_human_approve(approval_id: str) -> str:
    """(Simulated) Human approves a pending request."""
    if approval_id in pending_approvals:
        pending_approvals[approval_id]["status"] = ApprovalStatus.APPROVED
        return f"Approved: {approval_id}"
    return f"Not found: {approval_id}"


def simulate_human_reject(approval_id: str, reason: str) -> str:
    """(Simulated) Human rejects a pending request."""
    if approval_id in pending_approvals:
        pending_approvals[approval_id]["status"] = ApprovalStatus.REJECTED
        pending_approvals[approval_id]["reject_reason"] = reason
        return f"Rejected: {approval_id} — {reason}"
    return f"Not found: {approval_id}"


def main():
    print("Human-in-the-Loop Demo\n")

    agent = Agent(
        name="hr-agent",
        model="gemini-2.5-flash",
        description="HR assistant with approval workflow",
        instruction="""You are an HR assistant. For routine queries, respond directly.
        For high-stakes actions (sending bulk emails, modifying payroll, deleting records),
        use request_approval first. Wait for approval before confirming execution.""",
        tools=[
            FunctionTool(request_approval),
            FunctionTool(check_approval),
        ],
    )

    runner = Runner(agent=agent, session_service=InMemorySessionService())
    session = runner.session_service.create_session("hr", "hr-manager")

    # Step 1: Agent requests approval
    query = "Send a company-wide email about the new remote work policy"
    print(f"Manager: {query}\n")
    print("Agent: ", end="", flush=True)
    for event in runner.run(user_input=query, session=session):
        if event.content:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
    print()

    # Step 2: Simulate human review
    if pending_approvals:
        first_id = list(pending_approvals.keys())[0]
        print(f"\n--- Simulated Human Action ---")
        print(simulate_human_approve(first_id))
        print(f"--- Status After Approval ---")
        print(check_approval(first_id))


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Set GOOGLE_API_KEY environment variable to run.")
        exit(1)
    main()
