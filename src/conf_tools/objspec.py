from .code_desc import ConfToolsGlobal
from .code_specs import check_valid_code_spec, instantiate_spec
from .exceptions import (ConfToolsException, SemanticMistake, 
    SemanticMistakeKeyNotFound, SyntaxMistake)
from .load_entries import load_entries_from_dir
from .patterns import is_pattern, pattern_matches, recursive_subst
from .special_subst import substitute_special
from .utils import (can_be_pickled, expand_environment, expand_string, 
    friendly_path, indent, termcolor_colored)
from conf_tools import ID_FIELD, logger
from contracts import contract, describe_type, describe_value
from pprint import pformat
import os
import traceback



__all__ = [
    'ObjectSpec',
]


class ObjectSpec(dict):
    """ 
        This is the class that knows how to instance entries. 
        
        Users access it through ConfigMaster.
    
    """
    def __init__(self, name, pattern, check, instance_method, object_check, master):
        """
            Initializes the structure.
            
            :param:name: Decorative name for these objects (e.g. "vehicles")
            :param:pattern: Pattern for filenames ("*.vehicles.yaml")
            :param:check: Function to check the validity of the entries.
            :param:object_check: Function to check the validity of the values.
            :param:master: References to a Master instance. 
        """
        dict.__init__(self)

        self.name = name
        self.pattern = pattern
        self.user_check = check
        self.instance_method = instance_method
        self.object_check = object_check
        
        self.master = master

        # List of files already read        
        self.files_read = set()
        self.dirs_read = []
        self.dirs_to_read = []
        
        # ID -> file where it was found
        self.entry2file = {}

        self.templates = {}


        if not can_be_pickled(check):
            msg = 'Function %s passed as "check" cannot be pickled. ' % (check)
            msg += 'This might create problems later but it is OK to continue.'
            msg += ' Happened for %s/%s' % (master, self)
            # TODO: add where (2 levels up) 
            logger.warning(msg)

        if not can_be_pickled(instance_method):
            msg = ('Function %s passed as "instance_method" cannot be pickled. ' 
                   % instance_method)
            msg += 'This might create problems later but it is OK to continue.'
            msg += ' Happened for %s/%s' % (master, self)
            # TODO: add where (2 levels up)
            logger.warning(msg)

    def __repr__(self):
        return ('ObjectSpec(%s;fread:%s;dread:%s;dtoread:%s)' % 
                (self.name, self.files_read, self.dirs_read, self.dirs_to_read))
    
    def make_sure_everything_read(self):
        """ Reads the rest of the directories that we need to read. """
        while self.dirs_to_read:
            d = self.dirs_to_read.pop(0)
            self._actually_load(d)

    def load_config_from_directory(self, directory):
        """ 
            Puts the directory in the list of directories to read.
            It will be read only later, when triggered by make_sure_everything_read(). 
        """
        self.dirs_to_read.append(directory)
             
    def __iter__(self):
        self.make_sure_everything_read()
        return dict.__iter__(self)
        
    def keys(self):
        self.make_sure_everything_read()
        return dict.keys(self)
        
    @contract(key='str')
    def __contains__(self, key):
        self.make_sure_everything_read()
        return dict.__contains__(self, key) or self.matches_any_pattern(key)


    @contract(key='str')
    def __getitem__(self, key):
        self.make_sure_everything_read()
        # Check if it is available literally:
        if dict.__contains__(self, key):
            # Note: we copy
            return dict.__getitem__(self, key).copy()
        else:
            pattern = self.matches_any_pattern(key)
            if pattern is None:
                raise SemanticMistakeKeyNotFound(key, self)

            spec_template = self.templates[pattern]
            matches = pattern_matches(pattern, key)
            try:
                x = recursive_subst(spec_template, **matches)
                # We didn't do it before...
                dirname = os.path.dirname(self.entry2file[pattern])
                x = substitute_special(x, dirname=dirname)
                return x
            except (SyntaxMistake, SemanticMistake) as e:
                prefix = '    | '
                msg = ('%s\nError obtained while instantiating %r.\n'
                       'Pattern:\n%s'
                       '\nMatches:\n%s' % 
                       (e, pattern,
                        indent(pformat(spec_template), prefix),
                        indent(pformat(matches), prefix)
                       ))
                raise ConfToolsException(msg)

    @contract(key='str', returns='None|str')
    def matches_any_pattern(self, key):
        self.make_sure_everything_read()

        possibilities = []
        # Look for the template that can match the longer
        for template in self.templates:
            matches = pattern_matches(template, key)
            if matches:
                score = -sum(len(x) for x in matches.values())
                possibilities.append((score, template, matches))
                
        # no matches
        if not possibilities:
            return None
        
        # only one match
        if len(possibilities) == 1:
            return possibilities[0][1]
        
        # sort by score
        possibilities.sort(key=lambda p: (-p[0]))

        # Check if there is a tie
        best = possibilities[0][0]
        ties = [p[1] for p in possibilities if p[0] == best]
    
        if len(ties) >= 2:
            msg = ('Detected a tie. Key %r matches with same score: %r' % 
                   (key, ties))
            raise ValueError(msg)
        
#        if len(possibilities) >= 2:
#            for score, template, _ in possibilities:
#                print(' score: %s template %s' % (score, template))
#
#            print('best: %r' % possibilities[0][1])
#            
        return possibilities[0][1]
#        if not patterns:
#            return None
#        if len(patterns) > 1:
#            msg = ('Warning, the key %r is ambiguous because it matches '
#                   'more than one pattern; specifically, it matches the '
#                   'patterns %s. Aborting because this might have *very* '
#                   'unpredictable results.' % (key, ', '.join(patterns)))
#            raise ValueError(msg)
#        return patterns[0]

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

        # This actually instances the classes at read config time.
        # if self.user_check is not None:
        #     self.user_check(spec)

    @contract(id_object='str')
    def instance(self, id_object):
        """ Instances the entry with the given ID. """
        if not isinstance(id_object, str):
            raise ValueError('Expected string; got %r' % id_object)
        self.make_sure_everything_read()

        spec = self[id_object]
        try:
            value = self.instance_spec(spec)
        except Exception as e:
            msg = 'Could not instance the object %r\n' % id_object
            if id_object in self.entry2file:
                msg += 'defined at %s\n' % self.entry2file[id_object]
            else:
                msg += '(origin unknown)\n'
            msg += 'because of this error:\n'
            if isinstance(e, ConfToolsException):
                st = str(e)
            else:  
                st = traceback.format_exc(e)
            msg += indent(st.strip(), '| ')

            # from conf_tools.master import GlobalConfig

            # msg += '\n the conf is %s' % self
            
            raise ConfToolsException(msg)

        if self.user_check is not None:
            self.user_check(spec)
        return value

    @contract(spec='dict')
    def instance_spec(self, spec):
        """ Instances the given spec using the "instance_method" function. """
        self.make_sure_everything_read()

        if self.instance_method is None:
            msg = 'No instance method specified for %s.' % self.name
            raise ValueError(msg)
        return self.instance_method(spec)
        
    @contract(id_or_spec='str|dict', returns='tuple(str|None,*)')
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
        self.make_sure_everything_read()

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

    @contract(id_or_spec_or_code='str|dict|code_spec|*', returns='tuple(str|None,*)')
    def instance_smarter(self, id_or_spec_or_code):
        """ 
            Most flexible instantiation method. The parameter can be:
            - a string => id of spec
            - a spec (dict with fields: id, desc, and code) => it gets instantiated
            - a code spec (list of string, dict) => it gets called 
              In this case, the id returned is None.
            - an object, already instantiated. It is passed then through
                the check function.
                
        """
        self.make_sure_everything_read()

        if isinstance(id_or_spec_or_code, (str, dict)):
            id_or_spec = id_or_spec_or_code
            return self.instance_smart(id_or_spec)
        elif isinstance(id_or_spec_or_code, list):
            code_spec = id_or_spec_or_code
            check_valid_code_spec(code_spec) 
            ob = instantiate_spec(code_spec)
            return None, ob
        else:
            x = id_or_spec_or_code
            if self.object_check is None:
                msg = 'No check specified; cannot decide if valid: %s' % describe_type(x)
                raise ValueError(msg)
            else:
                try: 
                    self.object_check(x)
                except ValueError as e:
                    msg = 'Object %s not valid:\n%s' % (x, e)
                    raise ValueError(msg)
            return None, x

    def force_load(self, directory):
        """ Will force reloading of directory. """
        if directory in self.dirs_read:
            self.dirs_read.remove(directory)

        self.load_config_from_directory(directory)

    def _actually_load(self, directory):
        """ 
            Loads all files in the directory, recursively, using 
            the pattern specified in the constructor.
            Returns the number of new entries found.
        """
        if directory in self.dirs_read:
            # print('skipping directory %r because already read' % directory)
            return
        self.dirs_read.append(directory)
        
        from .global_config import dir_from_package_name, looks_like_package_name

        if looks_like_package_name(directory):
            # print('%r looks like a package' % directory)
            directory = dir_from_package_name(directory)
        else:
            # print('%r is plain looking' % directory)
            pass

        # print('actually loading directory %r for %s' % (directory, self.pattern))
        directory = expand_environment(directory)

        if not os.path.exists(directory):
            msg = 'Directory %r does not exist.' % directory
            raise SemanticMistake(msg)

        nfound = 0
        files = set()

        for where, x in load_entries_from_dir(directory, self.pattern):
            # logger.debug('loading %s:%s %s' % (where[0], where[1], x))
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
                
                if dict.__contains__(self, name):
                    old_entry =  dict.__getitem__(self, name)
                else:
                    assert name in self.templates
                    old_entry = self.templates[name]
                
                same_entry = (old_entry == x)
                if not (same_entry):
                    msg += '\nThey are different. The new one:'
                    msg += '\n' + indent(pformat(x), 'new |')
                    msg += '\nThe old one:'
                    msg += '\n' + indent(pformat(old_entry), 'old |')
                    raise SemanticMistake(msg)
                else:
                    msg += '\n(Ignoring because same)' 
                    logger.warn(msg)

            if is_pattern(name):
                self.templates[name] = x
            else:
                DESC_FIELD = 'desc'
                # If it only contains the "id" field, then we try
                # to instantiate it
                only_id = len(x.keys()) == 1
                only_id_and_desc = set(x.keys()) == set([ID_FIELD, DESC_FIELD]) 
                 
                if only_id or only_id_and_desc:
                    if not self.matches_any_pattern(name):
                        msg = ('While trying to instantiate empty entry %r '
                               'in %s, I could not find any pattern matching.'
                               % (name, friendly_path(filename)))
                        msg += '\nPatterns: %s' % self.templates
                        raise SemanticMistake(msg)

                    try:
                        x2 = self.__getitem__(name)
                    except ConfToolsException:
                        raise
                    assert x[ID_FIELD] == name
                    
                    if only_id_and_desc:
                        x2[DESC_FIELD] = x[DESC_FIELD]  
                    x = x2 
                    
                try:
                    self.check(x)
                except Exception as e:
                    msg = ("Error while checking the entry %r: %s" % 
                           (name, e))
                    msg += '\nEntry:\n' + indent(pformat(x), '  ')
                    msg += '\nException:\n' 
                    msg += indent(traceback.format_exc(e), '> ')
                    raise SemanticMistake(msg)

                dict.__setitem__(self, name, x)

            self.entry2file[name] = filename

            nfound += 1

        self.files_read.update(files)

        return nfound
    
    def summary_string_id_desc(self):
        """ Assuming that the entries are dictionaries
            with fields 'id' and 'desc', returns a summary string. 
        """
        self.make_sure_everything_read()

        s = ''
        keys = sorted(self.keys())
        if not keys:
            return ' (0 objects found)\n'
        maxlen = max([len(y) for y in keys])
        for x in keys:
            spec = self[x]
            if isinstance(spec, dict) and ('id' in spec) and ('desc' in spec):
                desc = spec['desc'].strip().replace('\n', ' ')
                s += '- %s: %s\n' % (x.rjust(maxlen), desc)
        return s 
        
    def summary_string_id_desc_patterns(self):
        """ Assuming that the entries are dictionaries
            with fields 'id' and 'desc', returns a summary string. 
        """
        self.make_sure_everything_read()

        s = self.summary_string_id_desc()        
        maxlen = max([len(y) for y in self.pattern])
        for x, spec in self.templates.items():
            if isinstance(spec, dict) and ('id' in spec) and ('desc' in spec):
                desc = spec['desc'].strip().replace('\n', ' ')
                s += '- %s: %s\n' % (x.rjust(maxlen), desc)
        return s 
    
    def _formatted_list_of_directories(self):
        
        def dirs():
            if not self.dirs_read:
                return '\nNo dirs read.'
            s = '\nDirs read:'
            for d in self.dirs_read:
                s += '\n- %s' % friendly_path(d)
            return s

        def dirs2():
            if not self.dirs_to_read:
                return '\nNo dirs to read.'
            s = '\nDirs to read:'
            for d in self.dirs_to_read:
                s += '\n- %s' % friendly_path(d)
            return s
        
        def files():
            if not self.files_read:
                return '\nNo files read (pattern: %s).' % self.pattern
            s = '\nFiles read:'
            for d in self.files_read:
                s += '\n- %s' % friendly_path(d)
            return s
        
        x = dirs() + files() + dirs2()
        
        # from conf_tools.master import GlobalConfig
        # x += '\n GlobalConfig dirs: %s' % GlobalConfig._dirs
        
        return x
        
    @contract(names='str|list(str)', returns='list(str)')
    def expand_names(self, names):
        """ 
            The most flexible expansion routine on the planet.
        
            Examples: ..
            
                config.widgets.expand_names('*')
                config.widgets.expand_names('a,b*')
                config.widgets.expand_names(['a','b*'])
                
        """
        self.make_sure_everything_read()

        if len(self) == 0 and len(self.templates) == 0:
            msg = 'No %s defined, cannot match names %s.' % (self.name, names)
            msg += self._formatted_list_of_directories()
            raise SemanticMistake(msg)
        
        if isinstance(names, str):
            names = [names]
        assert isinstance(names, list)
         
        try:
            options = self.keys()
            expanded = expand_string(names, options)
        except ValueError:
            expanded = []
            
        if not expanded:
            msg = 'Specified set %r of %s not found.' % (names, self.name)
            msg += ' Available %s: %s' % (self.name, options)
            raise SemanticMistake(msg)
    
        return expanded
    
    @contract(id_spec='str', desc='str', code='code_spec')
    def add_spec(self, id_spec, desc, code):
        """ Adds manually one spec. """
        self.make_sure_everything_read()

        spec = dict(id=id_spec, desc=desc, code=code)
        assert not id_spec in self
        # TODO: check doesn't exist
        self[spec['id']] = spec
    
    def print_summary(self, stream, instance=False, raise_instance_error=False):
        self.make_sure_everything_read()

        ConfToolsGlobal.log_instance_error = False  # XXX: find more elegant way # XXX: preserve
        
        stream.write('Spec %s:\n' % self.name)
        
        if self.files_read:
            stream.write('* Found %d config files:\n' % len(self.files_read))
            for filename in self.files_read:
                stream.write('  - %s\n' % filename)        
        else:
            stream.write('* No config file found.\n')    
        
        # if any entry defined...
        if len(self):
            stream.write('* Found %d objects: \n' % len(self))
    #         ordered = [(id_spec, self.specs[id_spec]) for id_spec in sorted(self.specs.keys())]
    #         
            for id_spec in self:
                desc = dict.__getitem__(id_spec).get('desc', '')
                
                # TODO: use first sentence
                # Get first line
                desc = desc.strip().split('\n')[0]
                 
                if desc == '':
                    desc = termcolor_colored('(no desc available)', color='grey')
                stream.write('  %40s:  %s\n' % (id_spec, desc))
                if instance:
                    try:
                        x = self.instance(id_spec)
                        xs = str(x)
                        xs = termcolor_colored(indent(xs, '    '), color='blue')
                    except Exception as e:  
                        if raise_instance_error:
                            raise
                        else:
                            xs = 'Could not instance object %r:\n' % id_spec
                            xs += indent(str(e), '| ') 
                            xs = termcolor_colored(indent(xs, '    '), color='red')
                            
                    stream.write(xs + '\n')
                #                     stream.write(' desc.
                # instance
        else:
            stream.write('* No objects found.\n')    
            
            
        if self.templates:  
            stream.write('* Found %d templates: \n' % len(self.templates))        
            for id_template in self.templates:
                stream.write('  - %s\n' % id_template)
        else:
            stream.write('* No templates found.\n')    
        
