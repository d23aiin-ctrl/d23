"""Pytest configuration."""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def anyio_backend():
    return "asyncio"
