# -*- coding: utf8 -*-

"""
The function in this Python module determines the current memory usage of the
current process by reading the VmSize value from /proc/$pid/status. It's based
on the following entry in the Python cookbook:
http://code.activestate.com/recipes/286222/
"""

import os

_units = { 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3 }
_handle = open('/proc/%d/status' % os.getpid())

def get_memory_usage():
    global _proc_status, _units, _handle
    try:
        for line in _handle:
            if line.startswith('VmSize:'):
                label, count, unit = line.split()
        return int(count) * _units[unit.upper()]
    except:
        return 0
    finally:
        _handle.seek(0)

def get_real_memory_usage():
    global _proc_status, _units, _handle
    try:
        for line in _handle:
            if line.startswith('VmRSS:'):
                label, count, unit = line.split()
        return int(count) * _units[unit.upper()]
    except:
        return 0
    finally:
        _handle.seek(0)
# vim: ts=2 sw=2 et
