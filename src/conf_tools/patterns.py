import re
from string import Template

reg = '\$\{([^\}]*)\}'


def is_pattern(s):
    isa = len(re.findall(reg, s)) > 0
#    if not isa:
#        print('Not a pattern: %r' % s)
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

    pmatch = '\A' + re.sub(reg, '(.*)', pattern) + '\Z'

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
        return Template(template).substitute(**matches)
    elif isinstance(template, list):
        return [recursive_subst(x, **matches) for x in template]
    elif isinstance(template, dict):
        return dict([k, recursive_subst(v, **matches)]
                    for k, v in template.items())
    else:
        return template



