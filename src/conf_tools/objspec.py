from . import (load_entries_from_dir, is_pattern, pattern_matches,
    recursive_subst, SemanticMistake, SemanticMistakeKeyNotFound, contract,
    describe_value, ID_FIELD, friendly_path, SyntaxMistake, ConfToolsException,
    logger)
from .utils import can_be_pickled, expand_string, indent
from UserDict import IterableUserDict
from pprint import pformat
import os
from conf_tools.utils import expand_environment
from conf_tools.special_subst import substitute_special
from conf_tools.code_desc import ConfToolsGlobal
import traceback

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

    @contract(key='str')
    def __contains__(self, key):
        return key in self.data or self.matches_any_pattern(key)

    @contract(key='str')
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
            try:
                x = recursive_subst(spec_template, **matches)
                # We didn't do it before...
                dirname = os.path.dirname(self.entry2file[pattern])
                x = substitute_special(x, dirname=dirname)
                return x
            except (SyntaxMistake, SemanticMistake) as e:
                prefix = '    | '
                msg = ('%s\nError obtained while instantiating %r.\nPattern:\n%s'
                       '\nMatches:\n%s' % 
                       (e, pattern,
                        indent(pformat(spec_template), prefix),
                        indent(pformat(matches), prefix)
                       ))
                raise ConfToolsException(msg)

    @contract(key='str', returns='None|str')
    def matches_any_pattern(self, key):
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

        if self.user_check is not None:
            self.user_check(spec)

    @contract(id_object='str')
    def instance(self, id_object):
        """ Instances the entry with the given ID. """
        self.master.make_sure_loaded()
        spec = self[id_object]
        try:
            return self.instance_spec(spec)
        except Exception as e:
            msg = 'Could not instance the object %r\n' % id_object
            if id_object in self.entry2file:
                msg += 'defined at %s\n' % self.entry2file[id_object]
#             msg += 'whose spec evaluates as\n'
#             msg += indent(pformat(spec), '| ') + '\n' 
            msg += 'because of this error:\n'
            msg += indent(traceback.format_exc(e).strip(), '> ')
            raise ConfToolsException(msg)        

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
        directory = expand_environment(directory)

        if not os.path.exists(directory):
            msg = 'Directory %r does not exist.' % directory
            raise SemanticMistake(msg)

        nfound = 0
        files = set()

        for where, x in load_entries_from_dir(directory, self.pattern):
#            logger.debug('loading %s:%s %s' % (where[0], where[1], x))
            filename = where[0]
            if filename in self.files_read:
                continue
            files.add(filename)

            name = x[ID_FIELD]
            # logger.debug('Found %s %r (%d concrete, %d patterns)' % 
            #              (self.name, name, len(self.data), len(self.templates)))

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

                    try:
                        x = self.__getitem__(name)
                    except ConfToolsException:
                        raise

                try:
                    self.check(x)
                except Exception as e:
                    raise SemanticMistake(e)

                self.data[name] = x

            self.entry2file[name] = filename

            nfound += 1

        self.files_read.update(files)

        return nfound
    
    def summary_string_id_desc(self):
        """ Assuming that the entries are dictionaries
            with fields 'id' and 'desc', returns a summary string. 
        """
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
        s = self.summary_string_id_desc()        
        maxlen = max([len(y) for y in self.pattern])
        for x, spec in self.templates.items():
            if isinstance(spec, dict) and ('id' in spec) and ('desc' in spec):
                desc = spec['desc'].strip().replace('\n', ' ')
                s += '- %s: %s\n' % (x.rjust(maxlen), desc)
        return s 
        
    @contract(names='str|list(str)', returns='list(str)')
    def expand_names(self, names):
        """ 
            The most flexible expansion routine on the planet.
        
            Examples: ..
            
                config.widgets.expand_names('*')
                config.widgets.expand_names('a,b*')
                config.widgets.expand_names(['a','b*'])
                
        """
        
        if len(self) == 0 and len(self.templates) == 0:
            msg = 'No %s defined, cannot match names %s.' % (self.name, names)
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
    
    def print_summary(self, stream, instance=False, raise_instance_error=False):
        ConfToolsGlobal.log_instance_error = False  # XXX: find more elegant way # XXX: preserve
        
        stream.write('Spec %s:\n' % self.name)
        
        if self.files_read:
            stream.write('* Found %d config files:\n' % len(self.files_read))
            for filename in self.files_read:
                stream.write('  - %s\n' % filename)        
        else:
            stream.write('* No config file found.\n')    
        
        if self.data:
            stream.write('* Found %d objects: \n' % len(self.data))
    #         ordered = [(id_spec, self.specs[id_spec]) for id_spec in sorted(self.specs.keys())]
    #         
            for id_spec in self.data:
                desc = self.data[id_spec].get('desc', '') 
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
        
