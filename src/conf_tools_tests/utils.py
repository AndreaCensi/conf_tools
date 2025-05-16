import os
import tempfile
from contextlib import contextmanager

from zuper_commons.test_utils import nottest

from conf_tools.master import GlobalConfig


@contextmanager
def create_tmp_dir():
    dirname = tempfile.mkdtemp()
    try:
        yield dirname
    except:
        raise


@nottest
@contextmanager
def create_test_environment(files):
    with create_tmp_dir() as dirname:
        GlobalConfig.clear_for_tests()
        for filename, contents in files.items():
            with open(os.path.join(dirname, filename), "w") as f:
                f.write(contents)

        yield dirname
