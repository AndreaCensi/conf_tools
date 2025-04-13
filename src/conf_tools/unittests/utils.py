from conf_tools.master import GlobalConfig
from contextlib import contextmanager
import os
import tempfile
import sys

# Try to import from nose, but provide a fallback for pytest compatibility
try:
    from nose.tools import nottest
except ImportError:
    # If nose is not available, create a compatible decorator
    def nottest(func):
        """Mark a function or method as not a test"""
        func.__test__ = False
        return func
        
    # Add a warning
    import warnings
    warnings.warn("nose is not installed; using compatible test utilities", 
                 ImportWarning)


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
            with open(os.path.join(dirname, filename), 'w') as f:
                f.write(contents)

        yield dirname
