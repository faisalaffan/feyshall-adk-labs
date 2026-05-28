"""Test suite entry point and shared fixtures."""
import pytest


@pytest.fixture(scope="session")
def requires_api_key():
    """Skip tests that need LLM access if no key is configured."""
    import os

    if not os.environ.get("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY not set")
    return True
