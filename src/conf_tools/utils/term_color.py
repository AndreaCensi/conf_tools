import sys

__all__ = [
    "termcolor_colored",
]

from zuper_commons.text import joinlines

try:
    from termcolor import colored as t_colored

    def termcolor_colored(s, color=None, on_color=None, attrs=None):
        return joinlines(t_colored(x, color, on_color, attrs) for x in s.splitlines())

except:
    # TODO: logger
    sys.stderr.write('compmake can make use of the package "termcolor".' " Please install it.\n")

    def termcolor_colored(x, color=None, on_color=None, attrs=None):  # @UnusedVariable
        """emulation of the termcolor interface"""
        return x
