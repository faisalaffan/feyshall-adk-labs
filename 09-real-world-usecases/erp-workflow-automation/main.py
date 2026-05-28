"""ERP Workflow Automation — multi-step approval chain.
Run: python 09-real-world-usecases/erp-workflow-automation/main.py
"""
import os
from enum import Enum
from dataclasses import dataclass, field
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()


def run_agent(agent, user_input: str, user_id: str) -> str:
    runner = Runner(agent=agent, session_service=session_service)
    session = session_service.create_session(agent.name, user_id)
    output = []
    for event in runner.run(user_input=user_input, session=session):
        if event.content:
            for part in event.content.parts:
                if part.text:
                    output.append(part.text)
    return "".join(output)


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class PurchaseRequest:
    id: str
    requester: str
    item: str
    quantity: int
    budget_per_unit: float
    justification: str
    manager_approval: ApprovalStatus = ApprovalStatus.PENDING
    finance_approval: ApprovalStatus = ApprovalStatus.PENDING
    procurement_status: str = ""

    @property
    def total(self) -> float:
        return self.quantity * self.budget_per_unit


requests_db: dict[str, PurchaseRequest] = {}


# Agent definitions
def create_purchase_request(item: str, quantity: int, budget_per_unit: float, justification: str) -> str:
    """Create a purchase request that needs manager + finance approval.

    Args:
        item: What to buy.
        quantity: How many.
        budget_per_unit: Price per unit in IDR.
        justification: Business reason for the purchase.
    """
    req_id = f"PR-{len(requests_db) + 1:04d}"
    pr = PurchaseRequest(
        id=req_id,
        requester="employee",
        item=item,
        quantity=quantity,
        budget_per_unit=budget_per_unit,
        justification=justification,
    )
    requests_db[req_id] = pr
    return (f"Purchase request {req_id} created.\n"
            f"Item: {quantity}x {item} @ Rp {budget_per_unit:,}/unit\n"
            f"Total: Rp {pr.total:,}\n"
            f"Status: Pending manager approval.")


def main():
    print("ERP Workflow Automation Demo\n")

    manager_agent = Agent(
        name="manager",
        model="gemini-2.5-flash",
        instruction="""Review purchase requests:
        Under Rp 1,000,000: auto-approve if justification is clear.
        Rp 1,000,000-10,000,000: approve with note about budget impact.
        Over Rp 10,000,000: flag for VP review.
        Always explain your decision.""",
    )

    finance_agent = Agent(
        name="finance",
        model="gemini-2.5-flash",
        instruction="""Review approved purchase requests:
        Check if budget is available.
        If total > Rp 5,000,000, suggest checking cheaper alternatives.
        Approve with budget code or flag for revision.""",
    )

    intake_agent = Agent(
        name="intake",
        model="gemini-2.5-flash",
        description="ERP purchase request intake",
        instruction="Collect purchase requests using create_purchase_request tool.",
        tools=[FunctionTool(create_purchase_request)],
    )

    # Step 1: Intake — create the request
    query = "We need 10 MacBook Pro laptops at Rp 25,000,000 each for the new engineering team starting next month"
    print(f"Employee: {query}\n")

    print("--- Stage 1: Intake ---")
    response = run_agent(intake_agent, query, "erp")
    print(response)

    if requests_db:
        pr_id = list(requests_db.keys())[0]
        pr = requests_db[pr_id]

        # Step 2: Manager review
        print("\n--- Stage 2: Manager Review ---")
        manager_response = run_agent(
            manager_agent,
            f"Review: {pr.item} x{pr.quantity} @ Rp {pr.budget_per_unit:,} = Rp {pr.total:,}. "
            f"Justification: {pr.justification}",
            "erp",
        )
        print(manager_response)

        # Step 3: Finance review
        print("\n--- Stage 3: Finance Review ---")
        finance_response = run_agent(
            finance_agent,
            f"Review approved purchase: {pr.item} x{pr.quantity}, Total: Rp {pr.total:,}",
            "erp",
        )
        print(finance_response)


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Set GOOGLE_API_KEY environment variable to run.")
        exit(1)
    main()
