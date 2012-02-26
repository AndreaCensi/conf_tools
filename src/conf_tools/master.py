from . import (is_pattern, pattern_matches, recursive_subst, logger,
    load_entries_from_file, locate_files)
from UserDict import IterableUserDict
from abc import abstractmethod
from contracts import contract, describe_value
from . import SemanticMistake
import os
from conf_tools.exceptions import SemanticMistakeKeyNotFound
from conf_tools.utils.friendly_paths import friendly_path


class ObjectSpec(IterableUserDict):
    """ 
        This is the class that knows how to instance entries. 
        
        Users access it through ConfigMaster.
    
    """
    def __init__(self, name, pattern, check, instance_method, master):
        """
            Initializes the structure.
            
            :param:name: Decorative name for these objects (e.g. "vehicles")
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

        # ID -> file where it was found
        self.entry2file = {}

        self.templates = {}

        IterableUserDict.__init__(self)

    def __contains__(self, key):
        return key in self.data or self.matches_any_pattern(key)

    def __getitem__(self, key):
        # Check if it is available literally:
        if key in self.data:
            # Note: we copy
            return self.data[key].copy()
        else:
            pattern = self.matches_any_pattern(key)
            if pattern is None:
                raise SemanticMistakeKeyNotFound(key, self)

            spec_template = self.templates[pattern]
            matches = pattern_matches(pattern, key)
            return recursive_subst(spec_template, **matches)
#
#    def get_normal_entries(self):
#        """ Returns the entries that aren't templates. """
#        return [x for x in self.data if not is_pattern(x)]

    def matches_any_pattern(self, key):
        patterns = [p for p in self.templates
                    if pattern_matches(p, key)]

        if not patterns:
            return None
        if len(patterns) > 1:
            msg = ('Warning, the key %r is ambiguous because it matches '
                   'more than one pattern; specifically, it matches the '
                   'patterns %s. Aborting because this might have *very* '
                   'unpredictable results.' % (key, ', '.join(patterns)))
            raise ValueError(msg)
        return patterns[0]

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
        return self.instance_spec(self[id_object])

    @contract(spec='dict')
    def instance_spec(self, spec):
        """ Instances the given spec using the "instance_method" function. """
        self.master.make_sure_loaded()
        if self.instance_method is None:
            msg = 'No instance method specified for %s.' % self.name
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
        if not os.path.exists(directory):
            msg = 'Directory %r does not exist.' % directory
            raise SemanticMistake(msg)
        nfound = 0
        for filename in locate_files(directory, self.pattern):
            #self.debug('Considering %r' % filename)
            if filename in self.files_read:
                #self.debug('Skipping %r' % filename)
                continue

            self.files_read.add(filename)

            entries = load_entries_from_file(filename, check_entry=self.check)

            for entry in entries:
                if entry in self.entry2file:
                    old_filename = self.entry2file[entry]
                    msg = ('Entry %r in\n  %s\n already found in\n  %s.'
                           % (entry, friendly_path(filename),
                              friendly_path(old_filename)))
                    raise SemanticMistake(msg)

            for entry in entries:
                if is_pattern(entry):
                    self.templates[entry] = entries[entry]
                else:
                    self.data[entry] = entries[entry]
                self.entry2file[entry] = filename

            nfound += len(entries)
        return nfound


class ConfigMaster:
    separator = ':'

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