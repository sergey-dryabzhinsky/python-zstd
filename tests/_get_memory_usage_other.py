# -*- coding: utf8 -*-

"""
The function in this Python module determines the current memory usage of the
current process by reading the VmSize value from /proc/$pid/status. It's based
on the following entry in the Python cookbook:
http://code.activestate.com/recipes/286222/
"""

# simulation for maxos and windows not having /proc
def get_memory_usage():
    return 0

def get_real_memory_usage():
    return 0
# vim: ts=2 sw=2 et
