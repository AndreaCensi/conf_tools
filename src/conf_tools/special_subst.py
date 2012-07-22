from . import SyntaxMistake, contract, describe_type, logger
import os


# TODO: put it somewhere
def recursive_subst_keys(struct, function):
    """ Recursive substitution in a structure
        for key/value pairs in dictionaries.
        function: (key, value) -> (key, value)  """
    if isinstance(struct, dict):
        # TODO: check no overwriting?
        return dict([function(k, recursive_subst_keys(v, function)) 
                     for k, v in struct.items()])
    elif isinstance(struct, list):
        return [recursive_subst_keys(x, function) for x in struct]
    else:
        return struct


@contract(entry='dict(str:*)', returns='dict(str:*)')
def substitute_special(entry, dirname):
    ''' Special stuff for "file:" and "file*" entries. '''
    function = lambda k, v: substitute_special_keys(k, v, dirname)
    newentry = recursive_subst_keys(entry, function)
    #logger.warn('from:\n%s\nto\n%s' % (pformat(entry), pformat(newentry)))
    return newentry

        
def substitute_special_keys(key, val, dirname):
    if not isinstance(key, str):
        return key, val
    if key.startswith('file:'):
        nkey = key[5:]
        nval = make_relative(val, dirname)
        check_exists(key, nval)
        return nkey, nval
    elif key.startswith('file'):
        nval = make_relative(val, dirname)
        check_exists(key, nval)
        return key, nval
    else:
        return key, val
    
            
def make_relative(val, dirname):
    if not isinstance(val, str):
        msg = ('Only strings can be used as keys, not %s.'
               % describe_type(val))
        raise SyntaxMistake(msg)
    joined = os.path.join(dirname, val)
    nval = os.path.realpath(joined)
    return nval


def check_exists(key, filename):
    if not os.path.exists(filename):
        msg = ('I resolved the key %r to the path\n\t%r\nbut it does not exist.'
               % (key, filename))
        logger.warning(msg)
               
