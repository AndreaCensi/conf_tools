from .objspec import ObjectSpec
from .utils import check_is_in
from conf_tools import logger
from contracts import contract


__all__ = ['ConfigMaster', 'GlobalConfig', 'ConfigState'] 


class GlobalConfig(object):
    """
    
        To correctly restore configuration with compmake: ::
        
        
            comp(f, GlobalConfig.get_state(), param=2)
        
            def f(config_state, param):
                config_state.restore()
                        
        
    """
    # A list 
    # str -> ConfigMaster
    _masters = {}
    
    # class -> instance of ObjSpec
    _singletons = {}
    
    # Directories previously loaded (in case somebody registers later)
    _dirs = []
    
    
        
    @staticmethod
    def register_master(name, master):
        """ 
            Register a master so that we can keep track of them,
            and load configuration in all of them at the same time. 
        """
        if not isinstance(name, str):
            raise ValueError('Required a string, got %s.' % name.__repr__())
         
        if name in GlobalConfig._masters:
            msg = 'Name %r already present.' % name
            raise ValueError(msg)
        
        GlobalConfig._masters[name] = master
        # print('registering %r' % name)
        
        for dirname in GlobalConfig._dirs:
            # print('Now deferred loading %r %r' % (name, dirname))
            master.load(dirname) 
    
    @staticmethod
    @contract(config_dirs='list(str)')
    def global_load_dirs(config_dirs):
        for c in config_dirs:
            GlobalConfig.global_load_dir(c)
        
    @staticmethod
    def global_load_dir(config_dir):
        """ 
            Load the configuration for all the different masters. 
            This could be a list of dirs separated by ":".
        """
        masters = GlobalConfig._masters

        for name, master in masters.items():  # @UnusedVariable
            # print('now loading %s / %s' % (name, config_dir))
            master.load(config_dir)
            
        logger.info('loaded global config dir %r' % config_dir)
        GlobalConfig._dirs.append(config_dir)
    
    @staticmethod
    def get_state():
        return ConfigState() 
    
    @staticmethod
    def set_state(state):
        state.restore()

    @staticmethod
    def clear_for_tests():
        """ Resets the state by unregistering everything; useful for tests. """
        GlobalConfig._masters = {}
        GlobalConfig._singletons = {}
        GlobalConfig._dirs = []
    
    
class ConfigState(object):
    
    def __init__(self):
        self.masters = GlobalConfig._masters
        self.singletons = GlobalConfig._singletons
        self.dirs = GlobalConfig._dirs
    
    def restore(self):
#         print('Restoring config state')
#         print('directories: %s' % self.dirs)
#         print('masters: %s' % self.masters)
#         print('singletons: %s' % self.singletons)
#         
      
        GlobalConfig._masters = self.masters
        GlobalConfig._dirs = self.dirs
        GlobalConfig._singletons = self.singletons
        
        

class ConfigMaster(object):
    
    @contract(name='str')
    def __init__(self, name):
        """
        
            :param:name: Name to use for logging messages. 
        """
        self.loaded = False
        self.specs = {}
        self.prefix = "%s: " % name if name else ""
        self.name = name

        # all the dirs that were passed to load(), in case we miss any
        self._dirs = []

        GlobalConfig.register_master(name, self)
        
    def __repr__(self):
        return 'ConfigMaster(%s,dirs=%s,specs=%s)' % (self.name, self._dirs, self.specs)
     
    def add_class(self, name, pattern, check=None, instance=None):
        '''
        Adds a type of objects.
        
        :param name:    Informative name
        :param pattern: Pattern for filenames.
        :param check:   spect -> {true, false} unction that checks whether a spec is correct 
        :param instance: spec -> object function
        '''
        spec = ObjectSpec(name, pattern, check, instance, self)
        self.specs[name] = spec
        self.__dict__[name] = spec
        
        for dirname in self._dirs:
            spec.load_config_from_directory(dirname)

        return spec
    
    
    def get_classes(self):
        """ Returns a list of strings of the known classes of objects. """
        # TODO: keep order
        return list(self.specs.keys())  
        
    def add_class_generic(self, name, pattern, object_class):
        if not '.yaml' in pattern or not '*' in pattern:
            logger.warning('suspicious pattern %r' % pattern)
        from .code_desc import GenericInstance
  
        return self.add_class(name=name, pattern=pattern, check=GenericCodeDescCheck(name),
                              instance=GenericInstance(object_class))

    def get_default_dir(self):
        logger.warning('No default dir given, using current dir.')
        return "."

    def make_sure_loaded(self):
        ''' 
            If the configuration is not been loaded yet, load the 
            default one. 
        '''
        if not self.loaded:
            self.load(None)

    @contract(dirs='list(str)')
    def load_dirs(self, dirs):
        for dirname in dirs:
            self.load(dirname)
            
    def load(self, directory=None):
        if directory == '':
            raise ValueError('Invalid directory name: %r' % directory)
        if directory is None or directory == 'default':
            directory = self.get_default_dir()

        if not isinstance(directory, str):
            msg = 'Expected a string for directory argument, got %s.' % type(directory)
            raise TypeError(msg)
        # self.debug('Loading config from %r.' % friendly_path(directory))

        if ConfigMaster.separator in directory:
            dirs = [x for x in directory.split(ConfigMaster.separator) if x]
            for d in dirs:
                self.load(d)
            return

        self._dirs.append(directory)

        self.loaded = True
        # found = []
        for spec in self.specs.values():
            # nfound = 
            spec.load_config_from_directory(directory)
            # found.append((spec.name, nfound))

        # lists = ', '.join('%d %s' % (b, a) for (a, b) in found)

        # msg = 'Found ' + lists + ' in %r.' % friendly_path(directory)
        # self.debug(msg)

    def debug(self, s):
        logger.debug('%s%s' % (self.prefix, s))

    def print_summary(self, stream, instance=False, only_type=None):
        """ Create a summary of all the configuration we have. """
        if only_type is None:
            ordered = [(id_spec, self.specs[id_spec]) for id_spec in sorted(self.specs.keys())]
            
            stream.write('Config has %d kinds of objects:\n ' % len(self.specs))
            for id_spec, spec in ordered:
                stream.write('%20s:  %d objects\n' % (id_spec, len(spec)))
            
            for id_spec, spec in ordered:
                stream.write('\n--- ')
                spec.print_summary(stream, instance=instance)    
        else:
            check_is_in('type', only_type, self.specs)
            spec = self.specs[only_type]
            spec.print_summary(stream, instance=instance)

    # used to separate directories in environment variable
    separator = ':'
    
    @classmethod
    def get_singleton(cls):
        if not cls in GlobalConfig._singletons:
            GlobalConfig._singletons[cls] = cls()
        return GlobalConfig._singletons[cls]

    @classmethod
    def set_singleton(cls, single):
        GlobalConfig._singletons[cls] = single
        

# TODO: move
class GenericCodeDescCheck():
    def __init__(self, name):
        self.name = name
    
    def __call__(self, x):
        from conf_tools.code_desc import check_generic_code_desc
        return check_generic_code_desc(x, self.name)

