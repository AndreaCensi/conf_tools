import re

from contracts import contract

from .exceptions import SemanticMistake, SyntaxMistake


__all__ = ['pattern_matches', 'recursive_subst', 'is_pattern']

reg = '\$\{([^\}]*)\}'


def is_pattern(s):
    if not isinstance(s, str):
        return False
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
            
        If the key contains 'id', it only matches [a-zA-Z]+\d*.
        
        For example:
        
            pattern_matches('Y${id_nuisance}${robot}', 'Yrp1R1')
            # -> {'id_nuisance': 'rp1', ... }

    """
    # reg = '\$\{([^\}]*)\}'
    reg = '\$\{([a-zA-Z_]\w*)\}'
    keys = re.findall(reg, pattern)

    if not keys:
        raise ValueError('Not a pattern: %r' % pattern)

    # The ? makes the match not greedy
    def make_pattern(match):
        key = match.group(1)
        if 'id' in key:
            # TODO: document this
            return '([a-zA-Z]+\d*)'
        else:
            return '(.+?)'
        
    pmatch = '\A' + re.sub(reg, make_pattern, pattern) + '\Z'
    
    m = re.match(pmatch, string)
    if m is None:
        # print('Not matched: %r %r' % (pattern, string))
        return None

    data = {}
    for i, key in enumerate(keys):
        data[key] = m.group(i + 1)

    return data


def recursive_subst(template, **matches):
    """ Recursive substitution """
    if isinstance(template, str):
#        return Template(template).substitute(**matches)
        # special case: "${x}" can be interpreted as a number
        s = substitute_strings(template, matches)
        s = s.strip()  # TODO: only if substitution
        return trynum(s)
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
        Raises SemanticMistake if key not found.
        SyntaxMistake if invalid format.
    """
    def sub(x):
        s, = x.groups(0)
        if not '|' in s:
            key = s
            if not key in matches:
                msg = 'Key %r not found (know %s)' % (key, matches.keys())
                raise SemanticMistake(msg)
            return matches[key]
        else:
            first = s.index('|')
            key = s[:first]
            expr = s[first + 1:]
            if not key in matches:
                msg = 'Key %r not found (know %s)' % (key, matches.keys())
                raise SemanticMistake(msg)

            value = trynum(matches[key])
            options = parse_options(expr)
            if not value in options:
                msg = ('Could not find value %r in options %s given for %r' % 
                       (value, options.keys(), key))
                raise SemanticMistake(msg)

            result = options[value]
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
            try:
                if x[0] == '[':
                    return eval(x)  # FIXME: tmp
                else:
                    return x
            except:
                return x


@contract(expr='str', returns='dict')
def parse_options(expr):
    """
        Parses a colon-separated list of a=b pair: ..
            
            a=1;b=2;c=3
         
    """
    def invalid():
        msg = 'Invalid options %r' % expr
        raise SyntaxMistake(msg)
    pairs = [s.strip() for s in expr.split(';')]
    options = {}
    for pair in pairs:
        if not '=' in pair:
            invalid()
        tokens = [x.strip() for x in pair.split('=')]
        if len(tokens) != 2:
            invalid()
        options[trynum(tokens[0])] = trynum(tokens[1])

    return options

