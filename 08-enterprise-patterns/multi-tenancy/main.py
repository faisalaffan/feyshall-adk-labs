"""Multi-Tenancy — tenant-isolated sessions and tools.
Run: python 08-enterprise-patterns/multi-tenancy/main.py
"""
import os


class TenantAwareSessionStore:
    """Namespaced session store — one tenant cannot access another's data."""

    def __init__(self):
        self._store: dict[str, dict] = {}

    def create(self, tenant_id: str, user_id: str) -> str:
        session_id = f"{tenant_id}:{user_id}"
        self._store[session_id] = {"tenant_id": tenant_id, "data": {}}
        return session_id

    def get(self, session_id: str, tenant_id: str) -> dict:
        if not session_id.startswith(f"{tenant_id}:"):
            raise PermissionError(
                f"Cross-tenant access denied: {tenant_id} → {session_id}"
            )
        return self._store.get(session_id, {})


class TenantScopedTool:
    """Tool that only accesses the current tenant's data."""

    def __init__(self, tenant_resolver):
        self.resolver = tenant_resolver

    def query(self, sql: str) -> list:
        tenant_id = self.resolver()
        print(f"  [Tool] Executing query as tenant '{tenant_id}'")
        print(f"  [Tool] SQL (with RLS): SELECT * FROM ({sql}) WHERE tenant_id='{tenant_id}'")
        return [{"id": 1, "tenant_id": tenant_id, "data": "result"}]


def main():
    print("Multi-Tenancy Demo\n")

    store = TenantAwareSessionStore()
    current_tenant = {"id": "tenant-a"}

    # Tenant A creates session
    session_a = store.create("tenant-a", "user-1")
    print(f"Tenant A session: {session_a}")

    # Tenant A accesses their own session → ok
    data = store.get(session_a, "tenant-a")
    print(f"✓ Tenant A reads own session: {data}\n")

    # Tenant B tries to access Tenant A's session → denied
    try:
        store.get(session_a, "tenant-b")
    except PermissionError as e:
        print(f"✗ {e}\n")

    # Tenant-scoped tool
    tool = TenantScopedTool(lambda: current_tenant["id"])
    print("Tenant A uses scoped tool:")
    tool.query("SELECT * FROM orders")

    # Switch tenant
    current_tenant["id"] = "tenant-b"
    print("\nTenant B uses same scoped tool:")
    tool.query("SELECT * FROM orders")


if __name__ == "__main__":
    main()
