from io import BytesIO
import pickle
import pytest
import os
import sys

# Add the src directory to the path for proper imports
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
sys.path.insert(0, src_dir)

# Import YAML compatibility layer
from conf_tools.unittests.yaml_compat import *

from conf_tools import ConfigMaster
from conf_tools.unittests.utils_pytest import create_test_environment

# Import the test cases directly, not as a relative import
from conf_tools.unittests.templating.simple_use_tests_pytest import test_cases


def dummy_check(spec):  # @UnusedVariable
    return True


def dummy_instance(spec):  # @UnusedVariable
    return True


def test_pickling():
    """Test that ConfigMaster can be pickled correctly."""
    # Create files
    with create_test_environment(test_cases[0]['config']) as dirname:
        # Load configuration
        master = ConfigMaster('veh')
        master.add_class('vehicles', '*.vehicles.yaml',
                         check=dummy_check,
                         instance=dummy_instance)
        master.load(dirname)
        s = BytesIO()
        pickle.dump(master, s)


if __name__ == "__main__":
    # Run this specific test file directly
    pytest.main(["-xvs", __file__])