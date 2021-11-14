import pickle
from io import BytesIO

from .templating.simple_use_tests import test_cases
from .utils import create_test_environment
from ..master import ConfigMaster


def dummy_check(spec):  # @UnusedVariable
    return True


def dummy_instance(spec):  # @UnusedVariable
    return True


def test_pickling():
    # Create files
    with create_test_environment(test_cases[0]["config"]) as dirname:
        # Load configuration
        master = ConfigMaster("veh")
        master.add_class("vehicles", "*.vehicles.yaml", check=dummy_check, instance=dummy_instance)
        master.load(dirname)
        s = BytesIO()
        pickle.dump(master, s)
