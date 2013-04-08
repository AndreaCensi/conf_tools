from contracts import contract
import re

__all__ = ['expand_string']


def flatten(seq):
    res = []
    for l in seq:
        res.extend(l)
    return res


@contract(x='str|list(str)', options='list(str)', returns='list(str)')
def expand_string(x, options):
    if isinstance(x, list):
        return flatten(expand_string(y, options) for y in x)
    elif isinstance(x, str):
        x = x.strip()
        if ',' in x:
            return flatten(expand_string(y, options) for y in x.split(','))
        elif '*' in x:
            expanded = list(expand_wildcard(x, options))
            return expanded
        else:
            return [x]
    else:
        assert False


def wildcard_to_regexp(arg):
    """ Returns a regular expression from a shell wildcard expression. """
    return re.compile('\A' + arg.replace('*', '.*') + '\Z')


@contract(wildcard='str', universe='list(str)')
def expand_wildcard(wildcard, universe):
    ''' 
        Expands a wildcard expression against the given list.
        
        :param wildcard: string with '*' 
        :param universe: a list of strings
    '''
    assert wildcard.find('*') > -1
    
    regexp = wildcard_to_regexp(wildcard)
    num_matches = 0
    for x in universe:
        if regexp.match(x):
            num_matches += 1
            yield x
        else:
            pass
            # print('%r does not match %r %r' % (x, wildcard, regexp))
    if num_matches == 0:
        msg = 'Could not find matches for pattern %r in %s.' % (wildcard, universe)
        print msg
        raise ValueError(msg)
