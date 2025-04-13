# -*- coding: utf-8 -*-
import pytest
import os
import sys

# Add the src directory to the path for proper imports
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Add shared fixtures here if needed