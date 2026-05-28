---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Multi-Tenancy

## Concept

In SaaS platforms, a single agent deployment serves multiple organizations (tenants). Each tenant needs isolated sessions, tools, and context — they must never see each other's data.

## Session Isolation

```python
from google.adk.sessions import SessionService

class TenantAwareSessionService:
    """Wraps session service to namespace sessions by tenant."""

    def __init__(self, backend_session_service):
        self.backend = backend_session_service

    def create_session(self, tenant_id: str, user_id: str) -> str:
        session_id = f"{tenant_id}:{user_id}"
        return self.backend.create_session(
            app_name=f"app-{tenant_id}",
            user_id=session_id,
        )

    def get_session(self, tenant_id: str, session_id: str):
        # Verify the session belongs to this tenant
        if not session_id.startswith(f"{tenant_id}:"):
            raise PermissionError("Cross-tenant access denied")
        return self.backend.get_session(session_id)
```

## Tool Isolation

```python
class TenantScopedTool:
    """Tool that only accesses the current tenant's data."""

    def __init__(self, tenant_resolver):
        self.resolver = tenant_resolver

    def query_database(self, sql: str) -> list:
        """Execute query scoped to current tenant."""
        tenant_id = self.resolver.current_tenant()
        # Enforce row-level security at query level
        scoped_sql = f"""
            SELECT * FROM ({sql}) AS q
            WHERE tenant_id = '{tenant_id}'
        """
        return execute(scoped_sql)
```

## Context Isolation

```python
class TenantContext:
    """Per-tenant context that agents can read but not cross."""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.config = load_tenant_config(tenant_id)
        self.rate_limits = load_rate_limits(tenant_id)
        self.custom_instructions = load_custom_instructions(tenant_id)

    def agent_instruction(self, base_instruction: str) -> str:
        """Augment agent instruction with tenant-specific rules."""
        return f"""
        {base_instruction}

        Tenant context:
        - Company: {self.config['company_name']}
        - Plan: {self.config['plan']}
        - Custom rules: {self.custom_instructions}
        """
```

## Architecture Checklist

- [ ] Sessions namespaced by tenant ID
- [ ] Tools enforce tenant scoping (not just trusting the agent)
- [ ] Database queries use row-level security (RLS)
- [ ] Rate limits per-tenant, not global
- [ ] Logging includes tenant ID for audit

## Pitfalls

- **Tenant ID in URL/prompt is NOT security**: An attacker can change the tenant ID. Always resolve tenant from the authenticated user, not user input.
- **Cross-tenant caching**: If you cache LLM responses, ensure cache keys include tenant ID. Otherwise Tenant A sees Tenant B's cached response.
- **Data residue**: When a tenant is deleted, clean up their sessions, memory store data, and cached embeddings. Automate this.
