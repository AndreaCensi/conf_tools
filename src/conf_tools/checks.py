from pprint import pformat

from contracts import contract, describe_type

from .exceptions import BadConfig


def wrap_check(x, what, function, *arg, **args):
    try:
        function(*arg, **args)
    except BadConfig as e:
        e.context('- While %s for structure:\n%s' % (what, pformat(x)))
        raise e


@contract(necessary='list(tuple(str,*))')
def check_necessary(x, necessary):
    for f, types in necessary:
        if not f in x:
            raise BadConfig(x, 'Field %r missing.' % f)
        if not isinstance(x[f], types):
            msg = ('Field %r must be one of %s, instead of %s.' % 
                   (f, types, describe_type(x[f])))
            raise BadConfig(x, msg)


def check_has_exactly_one(x, alternatives):
    found = []
    for f, types in alternatives:
        if f in x:
            found.append(f)
            if not isinstance(x[f], types):
                msg = ('Field %r must be one of %s, instead of %s.' % 
                       (f, types, describe_type(x[f])))
                raise BadConfig(x, msg)

    if not found:
        msg = ('The entry must have at least one in %r.' % 
                         [ft[0] for ft in alternatives])
        raise BadConfig(x, msg)

    if len(found) > 1:
        msg = ('The entry cannot have all of these together: %r' % found)
        raise BadConfig(x, msg)

