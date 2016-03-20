
__all__ = [
    'BadConfig', 
    'ConfToolsException',
    'SyntaxMistake', 
    'SemanticMistake', 
    'ResourceNotFound', 
    'SemanticMistakeKeyNotFound',
]

class BadConfig(Exception):

    def __init__(self, structure, complaint):
        self.structure = structure
        self.complaint = str(complaint)
        self.stack = []

    def context(self, structure):
        self.stack.append(structure)

    def __str__(self):
        from pprint import pformat
        s = '%s\n' % self.complaint
        s += 'Bad configuration snippet:\n%s\n\n' % pformat(self.structure)
        for x in self.stack:
            s += '%s\n' % x
        return s


class ConfToolsException(Exception):
    """ Error in the configuration (either syntax or semantics) """
    pass


class SyntaxMistake(ConfToolsException):
    """ For example, YAML mistakes, or file not containing dicts. """
    pass


class SemanticMistake(ConfToolsException):
    """ For example, repeated entries, or missing files/directories. """
    pass


class SemanticMistakeKeyNotFound(SemanticMistake):
    """ A spec has not been found. """
    def __init__(self, name, object_spec):
        # TODO: abbreviate
        # TODO: sort by similarity
        from . import ObjectSpec
        assert isinstance(object_spec, ObjectSpec)
        things = object_spec.name
        msg = ('The name %r does not match any %s. ' % (name, things))
        msg += '\nI know '
        found = dict.keys(object_spec)
        if found:
            found = sorted(list(found))
            msg += '%d entries (%s)' % (len(found), ", ".join(found))
        else:
            msg += '0 entries'
        msg += '\n'
        patterns = object_spec.templates.keys()
        if patterns:
            if found:
                msg += ' and the'
            else:
                msg += ' the'
            msg += ' templates %s.' % ", ".join(patterns)
        else:
            msg += ' and 0 templates.'
        
        msg += object_spec._formatted_list_of_directories()
        # TODO: sort by similarity
        # TODO: add "... and X others"
        SemanticMistake.__init__(self, msg)  # XXX: sure?


class ResourceNotFound(SemanticMistake):
    """ For example,  missing files/directories. """
    pass
