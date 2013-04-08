from conf_tools.utils.wildcards import expand_wildcard


def wildcard_test1():
    wildcard = 'unicornA_base1_*' 
    universe = ['unicornA_base1_2013-04-03-13-30-28', 'unicornA_base1_2013-04-06-19-44-59',
              'unicornA_base1_2013-04-03-13-16-53', 'unicornA_base1_2013-04-02-20-37-43',
              'unicornA_base1_all', 'unicornA_base1_2013-04-03-12-58-11',
              'unicornA_base1_2013-04-06-15-30-06', 'unicornA_base1_2013-04-03-16-36-03']

    res = list(expand_wildcard(wildcard, universe))
    
    print('Result: %s' % res)
