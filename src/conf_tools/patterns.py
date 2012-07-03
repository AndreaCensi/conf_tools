import re
from contracts import contract

__all__ = ['pattern_matches', 'recursive_subst', 'is_pattern']

reg = '\$\{([^\}]*)\}'


def is_pattern(s):
    isa = len(re.findall(reg, s)) > 0
    return isa


def pattern_matches(pattern, string):
    """ 
        Returns a dict with the substitutions. 
    
        For example, 
        
            pattern_matches('r-${robot}', 'r-ciao')
            # -> {'robot': 'ciao'}

            pattern_matches('r2-${robot}', 'r-ciao')
            # -> None
    """
    reg = '\$\{([^\}]*)\}'
    keys = re.findall(reg, pattern)

    if not keys:
        raise ValueError('Not a pattern: %r' % pattern)

    # The ? makes the match not greedy
    pmatch = '\A' + re.sub(reg, '(.*?)', pattern) + '\Z'

    m = re.match(pmatch, string)
    if m is None:
        #print('Not matched: %r %r' % (pattern, string))
        return None

    data = {}
    for i, key in enumerate(keys):
        data[key] = m.group(i + 1)

    return data


def recursive_subst(template, **matches):
    """ Recursive substitution """
    if isinstance(template, str):
#        return Template(template).substitute(**matches)
        #special case: "${x}" can be interpreted as a number
        return trynum(substitute_strings(template, matches))
    elif isinstance(template, list):
        return [recursive_subst(x, **matches) for x in template]
    elif isinstance(template, dict):
        return dict([k, recursive_subst(v, **matches)]
                    for k, v in template.items())
    else:
        return template


@contract(template='str', matches='dict(str:str)', returns='str')
def substitute_strings(template, matches):
    """
        Raises ValueError if key not found.
    """
    def sub(x):
        s, = x.groups(0)
        if not '|' in s:
            key = s
            if not key in matches:
                msg = 'Key %r not found (know %s)' % (key, matches.keys())
                raise ValueError(msg)
            return matches[key]
        else:
            first = s.index('|')
            key = s[:first]
            expr = s[first+1:]
            if not key in matches:
                msg = 'Key %r not found (know %s)' % (key, matches.keys())
                raise ValueError(msg)
            
            value = trynum(matches[key])
            options = parse_options(expr)
            if not value in options:
                msg = 'Could not find value %r in options %s' % (key, options.keys())
                raise ValueError(msg)
            
            result = options[value]
#            print('result: %r' % result)
            return str(result)
            
    return re.sub(reg, sub, template)
    
    
def trynum(x):
    """ Try to interpret x as a number """
    try:
        return int(x)
    except:
        try: 
            return float(x)
        except:
            return x
    

@contract(expr='str', returns='dict')
def parse_options(expr):
    """
        Parses a comma-separated list of a=b pair: ..
            
            a=1,b=2,c=3
         
    """
    def invalid():
        msg = 'Invalid options %r' % expr
        raise ValueError(msg)
    pairs = [s.strip() for s in expr.split(',')]
    options = {}
    for pair in pairs:
        if not '=' in pair:
            invalid()
        tokens = pair.split('=')
        if len(tokens) != 2:
            invalid()
        options[trynum(tokens[0])] = trynum(tokens[1])
    
    return options

