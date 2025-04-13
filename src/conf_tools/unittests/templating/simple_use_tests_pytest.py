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
from conf_tools.patterns import pattern_matches
from conf_tools.unittests.utils_pytest import create_test_environment

test_cases = [
    {'config': {
        'test.vehicles.yaml': '''
# A vehicle with a top and a bottom.
- id: "d-${top}-${bottom}"
  desc: "${top} / ${bottom}"
  code: code
                    '''},
        'query': 'd-TOP-BOTTOM',
        'result': dict(id="d-TOP-BOTTOM",
                       desc='TOP / BOTTOM', code='code')
    }
]

test_cases.append(dict(
                   config={'test.vehicles.yaml': """
- id: "s_rf_f${fov}n${n}d${disp}_n${noiselevel}"
  desc: Range-finder with ${disp|U=uniform;R=random} disposition.
  code: 
      - "vehicles.library.sensors.${disp|U=RangefinderUniform;R=RangefinderRandom}"
      - num_sensels: "${n}"
        fov_deg:     "${fov}"
        noise: 
            - vehicles.library.noises.AdditiveGaussian
            - std_dev: "${noiselevel|0=0;1=0.1;2=0.5}"
"""},
    query="s_rf_f180n180dU_n2",
    result=dict(id='s_rf_f180n180dU_n2',
            desc="Range-finder with uniform disposition.",
            code=["vehicles.library.sensors.RangefinderUniform",
                  dict(num_sensels=180, fov_deg=180,
                       noise=["vehicles.library.noises.AdditiveGaussian",
                              dict(std_dev=0.5)])])))


@pytest.mark.parametrize("test_case", test_cases)
def test_templating(test_case):
    """Test templating functionality."""
    config = test_case['config']
    query = test_case['query']
    result = test_case['result']
    
    # Create files
    with create_test_environment(config) as dirname:
        # Load configuration
        master = ConfigMaster('veh')
        master.add_class('vehicles', '*.vehicles.yaml')
        master.load(dirname)
        spec = master.specs['vehicles'][query]

        assert spec == result, (
            f"Expected {pformat(result)}, got {pformat(spec)}")


def test_basic_templating():
    """Test basic templating with pattern_matches."""
    result = pattern_matches('r-${robot}', 'r-ciao')
    assert result == dict(robot='ciao'), result

    result = pattern_matches('r2-${robot}', 'r-ciao')
    assert result is None, result


def test_ignoring_partial1():
    """Test that partial matches are ignored (case 1)."""
    result = pattern_matches('${robot}-nuisance', 'myrobot-nuisance-other')
    assert result is None, result


def test_ignoring_partial2():
    """Test that partial matches are ignored (case 2)."""
    result = pattern_matches('nuisance-${robot}', 'other-nuisance-myrobot')
    assert result is None, result


if __name__ == "__main__":
    # Run this specific test file directly
    pytest.main(["-xvs", __file__])