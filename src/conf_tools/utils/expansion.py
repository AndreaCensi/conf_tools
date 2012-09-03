import os
from contracts import contract

@contract(s='str')
def expand_environment(s):
    ''' Expands ~ and ${ENV} in the string. '''
    s = os.path.expandvars(s)
    s = os.path.expanduser(s)
    if '$' in s:
        msg = 'Unresolved env in %r' % s
        raise ValueError(msg)
    return s
