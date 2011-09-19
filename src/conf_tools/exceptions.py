from pprint import pformat

class BadConfig(Exception):
    # XXX: this is repeated in Vehicles
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
