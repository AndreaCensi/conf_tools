import pytest
import os
import sys

# Add the src directory to the path for proper imports
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
sys.path.insert(0, src_dir)

# Import YAML compatibility layer
from conf_tools.unittests.yaml_compat import *

from conf_tools.utils.wildcards import expand_wildcard


def test_wildcard_expansion():
    """Test wildcard expansion functionality."""
    wildcard = 'unicornA_base1_*' 
    universe = [
        'unicornA_base1_2013-04-03-13-30-28', 
        'unicornA_base1_2013-04-06-19-44-59',
        'unicornA_base1_2013-04-03-13-16-53', 
        'unicornA_base1_2013-04-02-20-37-43',
        'unicornA_base1_all', 
        'unicornA_base1_2013-04-03-12-58-11',
        'unicornA_base1_2013-04-06-15-30-06', 
        'unicornA_base1_2013-04-03-16-36-03'
    ]

    result = list(expand_wildcard(wildcard, universe))
    
    # Verify all items in universe are matched by the wildcard
    assert len(result) == len(universe)
    assert set(result) == set(universe)


if __name__ == "__main__":
    # Run this specific test file directly
    pytest.main(["-xvs", __file__])