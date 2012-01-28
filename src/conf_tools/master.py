from . import logger, load_entries_from_file, locate_files
from UserDict import IterableUserDict
from abc import abstractmethod
from contracts import contract, describe_value
from conf_tools.patterns import is_pattern, pattern_matches, recursive_subst


class ObjectSpec(IterableUserDict):
    """ 
        This is the class that knows how to instance entries. 
        
        Users access it through ConfigMaster
    
    """
    def __init__(self, name, pattern, check, instance_method, master):

        """
        
            :param:pattern: Pattern for filenames ("*.vehicles.yaml")
            :param:check: Function to check the validity of the entries.
            :param:master: References to a Master instance. 
        """
        self.name = name
        self.pattern = pattern
        self.user_check = check
        self.instance_method = instance_method
        self.master = master

        # List of files already read        
        self.files_read = set()

        IterableUserDict.__init__(self)


    def __contains__(self, key):
        return key in self.data or self.matches_any_pattern(key)

    def __getitem__(self, key):
        # Check if it is available literally:
        if key in self.data:
            return self.data[key]
        else:
            pattern = self.matches_any_pattern(key)
            if pattern is None:
                raise ValueError('Key %r does not match any pattern.' % key)

            spec_template = self.data[pattern]
            matches = pattern_matches(pattern, key)
            return recursive_subst(spec_template, **matches)

    def matches_any_pattern(self, key):
        for p in self.data:
            print('is_pattern: %s %s' % (p, is_pattern(p)))
            if is_pattern(p) and pattern_matches(p, key):
                return p
        return None


    def check(self, spec):
        """ 
            Checks that a spec is well formed, raises a ValueError if not.
            In addition to the user-defined check, it checks that there is 
            a "id" field.
        """
        if not isinstance(spec, dict):
            raise ValueError("I expect the spec to be a dict, not %s" %
                             describe_value(spec))

        if not 'id' in spec:
            msg = ('I expect the spec to contain a field "id"; found %s' %
                    describe_value(spec))
            raise ValueError(msg)

        if self.user_check is not None:
            self.user_check(spec)

    @contract(id_object='str')
    def instance(self, id_object):
        """ Instances the entry with the given ID. """
        self.master.make_sure_loaded()
        if not id_object in self.data:
            msg = ('No %s %r known; I know %s'
                    % (self.name, id_object, self.data.keys()))
            raise ValueError(msg)
        return self.instance_spec(self.data[id_object])

    @contract(spec='dict')
    def instance_spec(self, spec):
        """ Instances the given spec using the "instance_method" function. """
        self.master.make_sure_loaded()
        if self.instance_method is None:
            msg = 'No instance method specified for %r' % self.name
            raise ValueError(msg)
        return self.instance_method(spec)

    @contract(id_or_spec='str|dict')
    def instance_smart(self, id_or_spec):
        """ 
            Flexible instantiation method. The parameter can be either a 
            string or a dictionary. If it is a string, it must be the ID.
            If it is a dictionary, it must be a valid spec. The method
            returns a tuple (id, object).
            
            Example usage: ..
            
                id_dog, dog = config.specs['dogs'].instance_smart('puppy')
                
                spec = dict(id='puppy', class='Puppy')
                id_dog, dog = config.specs['dogs'].instance_smart(spec)
                
        """
        if isinstance(id_or_spec, str):
            return id_or_spec, self.instance(id_or_spec)
        elif isinstance(id_or_spec, dict):
            spec = id_or_spec
            self.check(spec)
            id_spec = spec['id']
            return id_spec, self.instance_spec(spec)
        else:
            msg = ('Expected string or dict, found %s.' %
                    describe_value(id_or_spec))
            raise ValueError(msg)

    def load_config_from_directory(self, directory):
        """ 
            Loads all files in the directory, recursively, using 
            the pattern specified in the constructor.
            Returns the number of new entries found.
        """
        nfound = 0
        for filename in locate_files(directory, self.pattern):
            #self.debug('Considering %r' % filename)
            if filename in self.files_read:
                #self.debug('Skipping %r' % filename)
                continue

            self.files_read.add(filename)

            entries = load_entries_from_file(filename, check_entry=self.check)

            for entry in entries:
                if entry in self.data:
                    msg = 'Entry %r already found.' % entry
                    raise ValueError(msg)

            self.data.update(entries)

            nfound += len(entries)
        return nfound





class ConfigMaster:

    def __init__(self, name=None):
        """
        
            :param:name: Name to use for logging messages. 
        """
        self.loaded = False
        self.specs = {}
        self.prefix = "%s: " % name if name else ""

    def add_class(self, name, pattern, check=None, instance=None):
        self.specs[name] = ObjectSpec(name, pattern, check, instance, self)
        self.__dict__[name] = self.specs[name]

    @abstractmethod
    def get_default_dir(self):
        pass

    def make_sure_loaded(self):
        ''' 
            If the configuration is not been loaded yet, load the default one. 
        '''
        if not self.loaded:
            self.load(None)

    def load(self, directory=None):
        if directory is None or directory == 'default':
            directory = self.get_default_dir()
        self.debug('Loading config from %r.' % directory)

        self.loaded = True
        found = []
        for spec in self.specs.values():
            nfound = spec.load_config_from_directory(directory)
            found.append((spec.name, nfound))
            # TODO: check redudancy

        lists = ', '.join('%s: %d' % (a, b) for (a, b) in found)
        self.debug('Found ' + lists + '.')

    def debug(self, s):
        logger.debug('%s%s' % (self.prefix, s))
