# ZSTD Library Python bindings
# Copyright (c) 2018, Sergey Dryabzhinsky and Zack Weinberg
# All rights reserved.
#
# BSD License
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
The functions in this module allow compression and decompression using
the zstandard library.

.. data:: VERSION

    Version of the Python bindings, as a string.

.. data:: LIBRARY_VERSION

    Version of the zstd library that this module was compiled against,
    as a string.

.. data:: LIBRARY_VERSION_NUMBER

    Version of the zstd library that this module was compiled against,
    as a number.
    The format of the number is: major*100*100 + minor*100 + release.

.. data:: CLEVEL_MIN

    Minimum compression level.

.. data:: CLEVEL_MAX

    Maximum compression level.

.. data:: CLEVEL_DEFAULT

    Default compression level.
"""

from __future__ import absolute_import
from . import _zstd

# preferred API
compress = _zstd.compress
decompress = _zstd.decompress

library_version = _zstd.library_version
library_version_number = _zstd.library_version_number

Error = _zstd.Error

VERSION = _zstd.VERSION
LIBRARY_VERSION = _zstd.LIBRARY_VERSION
LIBRARY_VERSION_NUMBER = _zstd.LIBRARY_VERSION_NUMBER

CLEVEL_MIN = _zstd.CLEVEL_MIN
CLEVEL_MAX = _zstd.CLEVEL_MAX
CLEVEL_DEFAULT = _zstd.CLEVEL_DEFAULT

__all__ = [ "compress", "decompress",
            "library_version", "library_version_number",
            "VERSION", "LIBRARY_VERSION", "LIBRARY_VERSION_NUMBER",
            "CLEVEL_MIN", "CLEVEL_MAX", "CLEVEL_DEFAULT",
            "Error" ]

# alternative names for compatibility
def _warn_deprecated_alt(old, new):
    import warnings
    warnings.warn("%s is deprecated, use %s instead" % (old, new),
                  DeprecationWarning)

def ZSTD_compress(data, level=3):
    "Deprecated alternative name for compress"
    _warn_deprecated_alt("ZSTD_compress", "compress")
    return compress(data, level)
def dumps(data, level=3):
    "Deprecated alternative name for compress"
    _warn_deprecated_alt("dumps", "compress")
    return compress(data, level)

def ZSTD_uncompress(data):
    "Deprecated alternative name for decompress"
    _warn_deprecated_alt("ZSTD_uncompress", "decompress")
    return decompress(data)
def uncompress(data):
    "Deprecated alternative name for decompress"
    _warn_deprecated_alt("uncompress", "decompress")
    return decompress(data)
def loads(data):
    "Deprecated alternative name for decompress"
    _warn_deprecated_alt("loads", "decompress")
    return decompress(data)

def version():
    "Deprecated alternative way to access the VERSION constant."
    _warn_deprecated_alt("version()", "VERSION")
    return VERSION

def ZSTD_version():
    "Deprecated alternative name for library_version"
    _warn_deprecated_alt("ZSTD_version", "library_version")
    return library_version()

def ZSTD_version_number():
    "Deprecated alternative name for library_version_number"
    _warn_deprecated_alt("ZSTD_version_number", "library_version_number")
    return library_version_number()

__all__.extend([ "ZSTD_compress", "dumps",
                 "ZSTD_uncompress", "uncompress", "loads",
                 "version", "ZSTD_version", "ZSTD_version_number" ])


if hasattr(_zstd, "compress_old"):
    def compress_old(data, level=3):
        import warnings
        warnings.warn(
            "compress_old produces an incompatible compressed data format",
            DeprecationWarning)
        return _zstd.compress_old(data, level)
    def decompress_old(data):
        import warnings
        warnings.warn(
            "decompress_old expects an incompatible compressed data format",
            DeprecationWarning)
        return _zstd.decompress_old(data)

    compress_old.__doc__ = _zstd.compress_old.__doc__
    decompress_old.__doc__ = _zstd.decompress_old.__doc__

    __all__.extend([ "compress_old", "decompress_old" ])
