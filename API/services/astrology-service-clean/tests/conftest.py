"""
Pytest Configuration and Fixtures.

Shared fixtures for all tests.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def anyio_backend():
    """Use asyncio for async tests."""
    return "asyncio"
