from pprint import pformat


class BadConfig(Exception):

    def __init__(self, structure, complaint):
        self.structure = structure
        self.complaint = str(complaint)
        self.stack = []

    def context(self, structure):
        self.stack.append(structure)

    def __str__(self):
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


class ResourceNotFound(SemanticMistake):
    """ For example,  missing files/directories. """
    pass
