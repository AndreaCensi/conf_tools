from . import (load_entries_from_dir, is_pattern, pattern_matches,
    recursive_subst, SemanticMistake, SemanticMistakeKeyNotFound, contract,
    describe_value, ID_FIELD, logger)
from .utils import friendly_path
from UserDict import IterableUserDict
import os

__all__ = ['ObjectSpec']


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
            msg = ("I expect the spec to be a dict, not %s" %
                    describe_value(spec))
            raise ValueError(msg)

        if not ID_FIELD in spec:
            msg = ('I expect the spec to contain a field "%r; found %s' %
                   (ID_FIELD, describe_value(spec)))
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
            id_spec = spec[ID_FIELD]
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
        files = set()

        for where, x in load_entries_from_dir(directory, self.pattern):
            #logger.debug('loading %s:%s %s' % (where[0], where[1], x))
            filename = where[0]
            if filename in self.files_read:
                continue
            files.add(filename)

            name = x[ID_FIELD]
            if name in self.entry2file:
                old_filename = self.entry2file[name]
                msg = ('Entry %r in\n  %s\n already found in\n  %s.'
                       % (name, friendly_path(filename),
                          friendly_path(old_filename)))
                raise SemanticMistake(msg)

            if is_pattern(name):
                self.templates[name] = x
            else:

                # If it only contains the "id" field, then we try
                # to instantiate it
                if len(x.keys()) == 1:
                    if not self.matches_any_pattern(name):
                        msg = ('While trying to instantiate empty entry %r '
                               'in %s, I could not find any pattern matching.'
                               % (name, friendly_path(filename)))
                        raise SemanticMistake(msg)

                    x = self.__getitem__(name)

                try:
                    self.check(x)
                except Exception as e:
                    raise SemanticMistake(e)

                self.data[name] = x

            self.entry2file[name] = filename

            nfound += 1

        self.files_read.update(files)

        return nfound
