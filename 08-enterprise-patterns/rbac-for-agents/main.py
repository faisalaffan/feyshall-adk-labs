"""RBAC for Agents — role-based access control demo.
Run: python 08-enterprise-patterns/rbac-for-agents/main.py
"""
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


class PermissionError(Exception):
    pass


def require_role(agent_name: str):
    """Decorator: enforce RBAC before agent execution."""

    def decorator(func):
        @wraps(func)
        def wrapper(user_role: Role, *args, **kwargs):
            allowed = AGENT_PERMISSIONS.get(agent_name, set())
            if user_role not in allowed:
                raise PermissionError(
                    f"User role '{user_role.value}' cannot access '{agent_name}'. "
                    f"Required: {[r.value for r in allowed]}"
                )
            return func(user_role, *args, **kwargs)

        return wrapper

    return decorator


# --- Simulated agent functions ---
@require_role("delete-data-agent")
def run_delete_agent(user_role: Role, input_text: str) -> str:
    return f"[DELETE] Executed: {input_text}"


@require_role("financial-report-agent")
def run_financial_agent(user_role: Role, input_text: str) -> str:
    return f"[FINANCE] Report generated for: {input_text}"


@require_role("faq-agent")
def run_faq_agent(user_role: Role, input_text: str) -> str:
    return f"[FAQ] Answering: {input_text}"


def main():
    print("RBAC for Agents Demo\n")

    test_cases = [
        (Role.ADMIN, "delete-data-agent", "Delete user #1234"),
        (Role.ANALYST, "delete-data-agent", "Delete user #5678"),
        (Role.MANAGER, "financial-report-agent", "Q2 revenue report"),
        (Role.VIEWER, "financial-report-agent", "Monthly summary"),
        (Role.VIEWER, "faq-agent", "What are your hours?"),
    ]

    for role, agent_name, query in test_cases:
        agent_map = {
            "delete-data-agent": run_delete_agent,
            "financial-report-agent": run_financial_agent,
            "faq-agent": run_faq_agent,
        }
        try:
            result = agent_map[agent_name](role, query)
            print(f"  ✓ [{role.value}] → {agent_name}: {result}")
        except PermissionError as e:
            print(f"  ✗ [{role.value}] → {agent_name}: DENIED — {e}")


if __name__ == "__main__":
    main()
