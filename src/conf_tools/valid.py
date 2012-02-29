from . import SyntaxMistake, is_pattern


def check_valid_id_or_pattern(name):
    ''' Check that name is either a valid ID or a valid pattern. '''
    if (not is_valid_id(name)) and (not is_pattern(name)):
        msg = 'The name %r is not a valid ID or pattern.' % name
        if (('$' in name) or ('(' in name) or (')' in name) or ('[' in name)
            or ('{' in name) or ('}' in name)):
            msg += ' Remember that patterns are written with curly braces '
            msg += '(e.g., "rsim-${VEHICLE}").'

        raise SyntaxMistake(msg)


def is_valid_id(entry):
    if ('$' in entry or '{' in entry or '}' in entry):
        return False
    # TODO: finish this
    return True

