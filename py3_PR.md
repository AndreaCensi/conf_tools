# Changes to conf_tools since commit 46b65eb

This file documents the changes made to conf_tools after commit 46b65ebc31700fcb51791645d017e6842f5e6706 as part of the Python 3 migration.

## Summary of Changes

- Modified PyContracts version requirement to support PyContracts 2.0.1
- Updated version from 1.9.9 to 1.9.10
- Set up as a new submodule in vendor directory

## Details

### 1. PyContracts Compatibility Fix

Modified `setup.py` to accept PyContracts 2.0.1:
- Changed `PyContracts>=1.2,<2` to `PyContracts>=1.2` to remove the upper version bound
- This allows using our Python 3.8+ compatible fork of PyContracts (v2.0.1)

### 2. Version Update

Updated version in `src/conf_tools/__init__.py`:
- Changed `__version__ = '1.9.9'` to `__version__ = '1.9.10'`

### 3. Repository Integration

Added as a new git submodule to the vendor directory:
- Note: This is not a forked repository but a clean clone from the original
- Can be later replaced with a proper fork if needed

### 4. Known Issues

The repository still has some outstanding issues:
- SyntaxWarnings for invalid escape sequences in regular expressions
- These are non-critical but should be fixed in a future update

This approach allows conf_tools to work with our updated PyContracts while maintaining its original functionality.