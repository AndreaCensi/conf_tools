import sys

__all__ = [
    "termcolor_colored",
]

from typing import List, Optional

from zuper_commons.text import joinlines

try:
    from termcolor import colored as t_colored

    def termcolor_colored(
        s: str, color: Optional[str] = None, on_color: Optional[str] = None, attrs: Optional[List[str]] = None
    ) -> str:
        return joinlines(t_colored(x, color, on_color, attrs) for x in s.splitlines())

except:
    # TODO: logger
    sys.stderr.write('compmake can make use of the package "termcolor".' " Please install it.\n")

    def termcolor_colored(
        s: str, color: Optional[str] = None, on_color: Optional[str] = None, attrs: Optional[List[str]] = None
    ) -> str:
        """emulation of the termcolor interface"""
        return s
