# -*- coding: utf8 -*-

"""
The function in this Python module determines the current memory usage of the
current process by reading the VmSize value from /proc/$pid/status. It's based
on the following entry in the Python cookbook:
http://code.activestate.com/recipes/286222/
"""

import platform

if platform.system()=='Linux':
    from ._get_memory_usage_linux import get_memory_usage, get_real_memory_usage
else:
    from ._get_memory_usage_other import get_memory_usage, get_real_memory_usage

# vim: ts=2 sw=2 et
