``ConfTools``: configuration made easy, for when it cannot be trivial
======================================================================

(To write)

Useful snippets
===============


Loading the YAML files that reside alongside the source code
------------------------------------------------------------

You can use ``resource_filename`` to find the directories
corresponding to the packages ``tmdp.configs`` in this way:

    from pkg_resources import resource_filename  
    dirs = [
        resource_filename("tmdp", "configs"),
        resource_filename("gridworld", "configs"),
    ]
    GlobalConfig.global_load_dirs(dirs)
