import pytest
import os
import sys

# Add the src directory to the path for proper imports
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../'))
sys.path.insert(0, src_dir)

# Import YAML compatibility layer
from conf_tools.unittests.yaml_compat import *

from conf_tools.instantiate_utils import import_name


class MyStatic:
    @staticmethod
    def f(a):
        return a + 1


def test_static_method_1():
    """Test importing a static method."""
    the_class = import_name('conf_tools.unittests.instantiate_tests.static_test_pytest.MyStatic')
    the_static = import_name('conf_tools.unittests.instantiate_tests.static_test_pytest.MyStatic.f')
    
    assert the_static(2) == 3


def test_not_existing():
    """Test that importing a non-existent module raises ValueError."""
    with pytest.raises(ValueError):
        import_name('not_existing.a')


def test_second():
    """Test that importing a non-existent attribute raises ValueError."""
    with pytest.raises(ValueError):
        import_name('conf_tools.a')


if __name__ == "__main__":
    # Run this specific test file directly
    pytest.main(["-xvs", __file__])