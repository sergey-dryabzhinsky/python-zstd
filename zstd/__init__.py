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
"""

from __future__ import absolute_import
from . import _zstd

# preferred API
compress = _zstd.compress
decompress = _zstd.decompress

version = _zstd.version
library_version = _zstd.library_version
library_version_number = _zstd.library_version_number

Error = _zstd.Error

# alternative names for compatibility
ZSTD_compress = compress
dumps = compress

ZSTD_uncompress = decompress
uncompress = decompress
loads = decompress

ZSTD_version = library_version
ZSTD_version_number = library_version_number

if hasattr(_zstd, "compress_old"):
    compress_old = _zstd.compress_old
    decompress_old = _zstd.decompress_old

__all__ = [ "compress", "decompress",
            "version", "library_version", "library_version_number",
            "Error" ]

__all__.extend([ "ZSTD_compress", "dumps",
                 "ZSTD_uncompress", "uncompress", "loads",
                 "ZSTD_version", "ZSTD_version_number" ])

if hasattr(_zstd, "compress_old"):
    __all__.extend([ "compress_old", "decompress_old" ])
