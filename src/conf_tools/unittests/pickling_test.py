from io import BytesIO
import pickle

from conf_tools import ConfigMaster
from conf_tools.unittests.utils import create_test_environment

from .templating.simple_use_tests import test_cases


def dummy_check(spec):  # @UnusedVariable
    return True

def dummy_instance(spec):  # @UnusedVariable
    return True

def test_pickling():
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
