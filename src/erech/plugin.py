import pytest
from erech import Have


@pytest.fixture
def have():
    """Provides the have instance for assertions."""
    return Have()


