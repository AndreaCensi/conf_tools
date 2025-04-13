from conf_tools.master import GlobalConfig
from contextlib import contextmanager
import pytest
import os
import tempfile


@contextmanager
def create_tmp_dir():
    """Create a temporary directory for testing."""
    dirname = tempfile.mkdtemp()
    try:
        yield dirname
    finally:
        # Note: we're not cleaning up the temp dir to make test debugging easier
        # For automatic cleanup, use pytest's tmp_path fixture instead
        pass


@pytest.mark.skip("This is a test helper, not a test")
@contextmanager
def create_test_environment(files):
    """Create a test environment with specified files.
    
    Args:
        files: Dictionary of filename -> content mappings
        
    Yields:
        Directory name of created test environment
    """
    with create_tmp_dir() as dirname:
        GlobalConfig.clear_for_tests()
        for filename, contents in files.items():
            with open(os.path.join(dirname, filename), 'w') as f:
                f.write(contents)

        yield dirname