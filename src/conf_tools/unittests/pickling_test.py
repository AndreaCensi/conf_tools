from StringIO import StringIO
from conf_tools.unittests.utils import create_test_environment
from conf_tools.master import ConfigMaster
import pickle
from conf_tools.unittests.templating.simple_use_tests import test_cases

def dummy_check(spec):
    return True

def dummy_instance(spec):
    return True

def test_pickling():
    # Create files
    with create_test_environment(test_cases[0]['config']) as dirname:
        # Load configuration
        master = ConfigMaster()
        master.add_class('vehicles', '*.vehicles.yaml',
                         check=dummy_check,
                         instance=dummy_instance)
        master.load(dirname)
        s = StringIO()
        pickle.dump(master, s)
