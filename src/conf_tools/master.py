from . import ObjectSpec, logger
from .utils import friendly_path


class ConfigMaster:

    # used to separate directories in environment variable
    separator = ':'

    def __init__(self, name=None):
        """
        
            :param:name: Name to use for logging messages. 
        """
        self.loaded = False
        self.specs = {}
        self.prefix = "%s: " % name if name else ""

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
        return spec
    
    def add_class_generic(self, name, pattern, object_class):
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

    def load(self, directory=None):
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

        self.loaded = True
        found = []
        for spec in self.specs.values():
            nfound = spec.load_config_from_directory(directory)
            found.append((spec.name, nfound))

        lists = ', '.join('%d %s' % (b, a) for (a, b) in found)

        msg = 'Found ' + lists + ' in %r.' % friendly_path(directory)
        self.debug(msg)

    def debug(self, s):
        logger.debug('%s%s' % (self.prefix, s))


    def print_summary(self, stream, instance=False):
        """ Create a summary of all the configuration we have. """
        
        ordered = [(id_spec, self.specs[id_spec]) for id_spec in sorted(self.specs.keys())]
        stream.write('Config has %d kinds of objects:\n ' % len(self.specs))
        for id_spec, spec in ordered:
            stream.write('%20s:  %d objects\n' % (id_spec, len(spec)))
        
        for id_spec, spec in ordered:
            stream.write('\n--- ')
            spec.print_summary(stream, instance=instance)    
            
             


# TODO: move
class GenericCodeDescCheck():
    def __init__(self, name):
        self.name = name
    
    def __call__(self, x):
        from conf_tools.code_desc import check_generic_code_desc
        return check_generic_code_desc(x, self.name)

