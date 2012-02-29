import tempfile
from contextlib import contextmanager
import os
from nose.tools import nottest


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
        for filename, contents in files.items():
            with open(os.path.join(dirname, filename), 'w') as f:
                f.write(contents)

        yield dirname
