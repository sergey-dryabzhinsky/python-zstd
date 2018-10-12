===========
python-zstd
===========

.. image:: https://travis-ci.org/sergey-dryabzhinsky/python-zstd.svg?branch=master
    :target: https://travis-ci.org/sergey-dryabzhinsky/python-zstd

Simple python bindings for Yann Kollet’s Zstandard compression
library.

Zstandard, or Zstd for short, is a new lossless compression algorithm,
intended to provide compression ratios at least as good as zlib while
being significantly faster.  It can also produce compression ratios
competitive with bzip2 and lzma, at the cost of compression speed,
but preserving the same high *decompression* speed.

Both `these bindings`_ and the `reference C implementation`_ of
Zstandard are hosted on GitHub.

.. _these bindings: https://github.com/sergey-dryabzhinsky/python-zstd
.. _reference C implementation: https://github.com/facebook/zstd

These python bindings are kept simple.  They provide functionality
comparable to the various compression modules in the Python standard
library.  In particular, we do not plan to support compression
dictionaries nor any of the experimental APIs provided by the
reference C implementation of Zstandard (libzstd).  The `zstandard`_
module, maintained by Gregory Szorc, provides access to these features
at the cost of a much more elaborate API.

.. _zstandard: https://pypi.python.org/pypi/zstandard

COMPATIBILITY WARNINGS
----------------------

If this module is built with legacy format support enabled, it can
decompress data compressed by any published version of Zstandard, all
the way back to libzstd version 0.1.  If not, it can only decompress
data in the standardized format produced by libzstd version 0.8 and
later.

The compressed data format produced by old versions of this module
(prior to 1.0.0.99.1) used a custom header that other consumers of
Zstd-compressed data cannot read.  If you have data in this format,
you should build this module with legacy format support enabled,
decompress the data with ``zstd.decompress_old``, and recompress it
with ``zstd.compress``.  Support for the old custom header may be
removed in a future release of these bindings.

Install from pypi
-----------------

Source packages are available from PyPI for Python 2.6+::

   $ pip install zstd

and for Python 3.2+::

   $ pip3 install zstd

Precompiled packages are not currently available; these commands will
fail if a C compiler, Python development headers, or `setuptools`_ are
not available on the system.  On Debian-like Linux distributions, to
build for Python 2::

   $ sudo apt-get install build-essential python-dev python-setuptools

or for Python 3::

   $ sudo apt-get install build-essential python3-dev python3-setuptools

.. _setuptools: https://pypi.org/project/setuptools/

Installations from PyPI use a bundled libzstd and do not support
legacy formats.

Building from Git
-----------------

Check out the code::

   $ git clone https://github.com/sergey-dryabzhinsky/python-zstd
   $ cd python-zstd
   $ git submodule update --init

The same tools are required as for building from PyPI.

::

   $ python setup.py build_ext test
   $ python3 setup.py build_ext test

Parallel builds are supported for Python 3.5 and later.

::

   $ python3 setup.py build_ext -j8

Legacy format support is disabled by default.  To build with legacy
format support, pass the ``--legacy`` option to ``setup.py``::

   $ python setup.py build_ext --legacy test

To use an externally supplied copy of libzstd, pass the ``--external``
option to ``setup.py``::

   $ sudo apt-get install libzstd-dev
   $ python setup.py build_ext --external test

The external libzstd must be version 1.3.4 or later.  Legacy format
support cannot be enabled when using an external libzstd.

``setup.py`` will attempt to use ``pkg-config`` to locate an external
libzstd; failing that, it will assume that the header file ``zstd.h``
and library file ``-lzstd`` are available without special compile-time
options.  If this is incorrect, you can use the ``--libraries``,
``--include-dirs``, and ``--library-dirs`` options to tell it where to
look::

   $ python setup.py build_ext --external \
       --include-dirs /opt/zstd/usr/include \
       --library-dirs /opt/zstd/lib \
       --libraries zstd

Basic usage
-----------

Compression and decompression are the same as with ``zlib``:

   >>> import zstd
   >>> data = b"123456qwert"
   >>> cdata = zstd.compress(data, level=1)
   >>> data == zstd.decompress(cdata)
   True

The ``level`` parameter to ``zstd.compress`` can be any integer from
``zstd.CLEVEL_MIN`` (currently −5) to ``zstd.CLEVEL_MAX``
(currently 22).  Omitting it, or passing zero, is the same as passing
``zstd.CLEVEL_DEFAULT`` (currently 3).  Negative numbers compress
“ultra-fast,” at the expense of compression ratio.  Numbers greater
than or equal to 20 produce “ultra-high” compression ratios, at the
expense of speed and memory usage.

The version of these bindings is exposed as ``zstd.VERSION``.

   >>> zstd.VERSION
   '1.3.5.1'

The first three elements of this number are the version of libzstd
that was bundled with the package, even if you built using an external
libzstd with a different version.  The fourth element counts updates
to the bindings in between updates to the bundled libzstd.

The actual libzstd version compiled against is
``zstd.LIBRARY_VERSION``, and the actual libzstd version in use at
runtime is ``zstd.library_version()``.

   >>> zstd.LIBRARY_VERSION
   '1.3.5'
   >>> zstd.library_version()
   '1.3.6'

This is what you would see if the module had been compiled against
version 1.3.5 of an external libzstd, but then the library was updated
to 1.3.6.
