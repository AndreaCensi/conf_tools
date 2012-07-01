from . import ObjectSpec, logger
from .utils import friendly_path


class ConfigMaster:
#    __metaclass__ = ABCMeta

    # used to separate directories
    separator = ':'

    def __init__(self, name=None):
        """
        
            :param:name: Name to use for logging messages. 
        """
        self.loaded = False
        self.specs = {}
        self.prefix = "%s: " % name if name else ""

    def add_class(self, name, pattern, check=None, instance=None):
        spec = ObjectSpec(name, pattern, check, instance, self)
        self.specs[name] = spec
        self.__dict__[name] = spec
        return spec

#    @abstractmethod
    def get_default_dir(self):
        logger.warning('No default dir given, using current dir.')
        return "."
#        pass

    def make_sure_loaded(self):
        ''' 
            If the configuration is not been loaded yet, load the 
            default one. 
        '''
        if not self.loaded:
            self.load(None)

    def load(self, directory=None):
        if directory is None or directory == 'default':
            directory = self.get_default_dir()

        #self.debug('Loading config from %r.' % friendly_path(directory))

        if ConfigMaster.separator in directory:
            dirs = [x for x in directory.split(ConfigMaster.separator) if x]
            for d in dirs:
                self.load(d)
            return

        self.loaded = True
        found = []
        for spec in self.specs.values():
            nfound = spec.load_config_from_directory(directory)
            found.append((spec.name, nfound))

        lists = ', '.join('%d %s' % (b, a) for (a, b) in found)

        msg = 'Found ' + lists + ' in %s.' % friendly_path(directory)
        self.debug(msg)

    def debug(self, s):
        logger.debug('%s%s' % (self.prefix, s))
