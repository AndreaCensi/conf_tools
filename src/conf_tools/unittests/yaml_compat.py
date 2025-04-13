"""
YAML compatibility module for Python 3.12
"""
import sys
import yaml
import types
import functools

# Monkey patch yaml.load to include the SafeLoader by default
original_yaml_load = yaml.load

@functools.wraps(original_yaml_load)
def safe_yaml_load(stream, Loader=None):
    """Wrapper for yaml.load that uses SafeLoader by default"""
    if Loader is None:
        Loader = yaml.SafeLoader
    return original_yaml_load(stream, Loader)

# Apply the patch for tests
yaml.load = safe_yaml_load