import pytest
from pprint import pformat
import os
import sys

# Add the src directory to the path for proper imports
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../'))
sys.path.insert(0, src_dir)

# Import YAML compatibility layer
from conf_tools.unittests.yaml_compat import *

from conf_tools.master import ConfigMaster
from conf_tools.unittests.utils_pytest import create_test_environment
from conf_tools.exceptions import ConfToolsException

other_tests = [
    {
      'good': False,
      'what': "Empty template reference with no template",
      'config': {
        'data1.things.yaml': """

- id: my-stuff
                
        """
       }
    },
    {
      'good': True,
      'what': "Good template",
      'config': {
        'data1.things.yaml': """

- id: "my-${thing}"
  desc: "${thing} instance"
   
- id: my-stuff
        """
       },
       'should_have': ['my-stuff']
    },
    {
      'good': True,
      'what': "Check the template is not in the list.",
      'config': {
        'data1.things.yaml': """

- id: "my-${thing}"
  desc: "${thing} instance"
   
        """
       },
       'should_have': []
    }
]


@pytest.mark.parametrize("test_case", [tc for tc in other_tests if tc['good']])
def test_templating_good(test_case):
    """Test good templating cases."""
    check_can_be_loaded(test_case)


@pytest.mark.parametrize("test_case", [tc for tc in other_tests if not tc['good']])
def test_templating_bad(test_case):
    """Test bad templating cases."""
    with pytest.raises(ConfToolsException):
        check_can_be_loaded(test_case)


def check_can_be_loaded(tc):
    """Helper function to load configuration and check results."""
    # Create files
    with create_test_environment(tc['config']) as dirname:
        master = ConfigMaster('veh')

        def check_entry(entry):
            if 'desc' not in entry:
                raise ValueError('No desc field')

        master.add_class('things', '*.things.yaml', check=check_entry)
        master.load(dirname)
        master.specs['things'].make_sure_everything_read()

        should_have = tc.get('should_have', None)
        if should_have is not None:
            found = set(master.specs['things'].keys())
            assert set(should_have) == found, (
                f"Expected {should_have}, obtained {found}")


if __name__ == "__main__":
    # Run this specific test file directly
    pytest.main(["-xvs", __file__])