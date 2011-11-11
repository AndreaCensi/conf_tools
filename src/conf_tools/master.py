from . import load_configuration_entries, logger 
from UserDict import IterableUserDict
from abc import abstractmethod
from contracts import contract

class ObjectSpec(IterableUserDict):
    def __init__(self, name, pattern, check, instance_method, master):
        self.name = name
        self.pattern = pattern
        self.check = check
        self.instance_method = instance_method
        self.master = master
        IterableUserDict.__init__(self)

    @contract(id_object='str')
    def instance(self, id_object):
        self.master.make_sure_loaded()
        if not id_object in self.data:
            msg = ('No %s %r known; I know %s'  
                    % (self.name, id_object, self.data.keys()))
            raise ValueError(msg)
        return self.instance_spec(self.data[id_object])
    
    @contract(spec='dict')
    def instance_spec(self, spec):
        self.master.make_sure_loaded()
        if self.instance_method is None:
            msg = 'No instance method specified for %r' % self.name
            raise ValueError(msg)
        return self.instance_method(spec)
        

class ConfigMaster:
    
    def __init__(self, name=None):
        self.loaded = False
        self.specs = {}
        self.prefix = "%s: " % name if name else "" 
        
    def add_class(self, name, pattern, check=None, instance=None):
        self.specs[name] = ObjectSpec(name, pattern, check, instance, self)
        
    @abstractmethod
    def get_default_dir(self):
        pass
    
    def make_sure_loaded(self):
        ''' If the configuration is not been loaded yet, load the default one. '''
        if not self.loaded:
            self.load(None)
        
    def load(self, directory=None):
        if directory is None:
            directory = self.get_default_dir()
        logger.debug('%sLoading config from %r.' % (self.prefix, directory))

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
            
        lists = ', '.join('%s: %d' % (a, b) for (a, b) in found) 
        message = 'Found ' + lists + '.'
        logger.debug('%s%s' % (self.prefix, message))
