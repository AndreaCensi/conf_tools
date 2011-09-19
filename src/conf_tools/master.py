from . import load_configuration_entries, logger
from UserDict import IterableUserDict
from abc import abstractmethod


class ObjectSpec(IterableUserDict):
    def __init__(self, name, pattern, check, instance_method):
        self.name = name
        self.pattern = pattern
        self.check = check
        self.instance_method = instance_method
        IterableUserDict.__init__(self)

    def instance(self, id_object):
        return self.instance_spec(self.data[id_object])
      
    def instance_spec(self, spec):
        if self.instance_method is None:
            msg = 'No instance method specified for %r' % self.name
            raise ValueError(msg)
        return self.instance_method(spec)
        

class ConfigMaster:
    
    def __init__(self):
        self.loaded = False
        self.specs = {}
        
    def add_class(self, name, pattern, check=None, instance=None):
        self.specs[name] = ObjectSpec(name, pattern, check, instance)
        
    @abstractmethod
    def get_default_dir(self):
        pass
    
    def load(self, directory=None):
        if directory is None:
            directory = self.get_default_dir()

        logger.debug('Reading %s' % directory)
        self.loaded = True
        found = []
        for spec in self.specs.values():
            pattern = spec.pattern
            check = spec.check
            entries = load_configuration_entries(directory, pattern=pattern,
                                       check_entry=check)
            found.append((spec.name, len(entries)))
            # TODO: check redudancy
            spec.data.update(entries)
            
        lists = ', '.join('%d %s(s)' % (b, a) for (a, b) in found) 
        message = 'Found ' + lists + '.'
        logger.debug(message)
