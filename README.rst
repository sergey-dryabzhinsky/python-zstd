=============
python-zstd
=============

.. image:: https://travis-ci.org/sergey-dryabzhinsky/python-zstd.svg?branch=master
    :target: https://travis-ci.org/sergey-dryabzhinsky/python-zstd

Python bindings to Yann Collet ZSTD compression library

**Zstd**, short for Zstandard, is a new lossless compression algorithm,
 which provides both good compression ratio _and_ speed for your standard compression needs.
 "Standard" translates into everyday situations which neither look for highest possible ratio
 (which LZMA and ZPAQ cover) nor extreme speeds (which LZ4 covers).

It is provided as a BSD-license package, hosted on GitHub_.

.. _GitHub: https://github.com/facebook/zstd

TODO
----

1. Support dictionary training. Current status is ``not supported``.


Build from source
-----------------

   >>> git clone https://github.com/sergey-dryabzhinsky/python-zstd
   >>> git submodule update --init
   >>> apt-get install python-dev python3-dev python-setuptools python3-setuptools
   >>> python setup.py build_ext clean
   >>> python3 setup.py build_ext clean

Note: legacy format support disabled by default.
To build with legacy support - pass ``--legacy`` option to setup.py script:

   >>> python setup.py build_ext --legacy clean

If you want to build with existing distribution of libzstd just add ``--external`` option.
But beware! Legacy formats support is unknown in this case.

   >>> python setup.py build_ext --external clean

If paths to header file ``zstd.h`` and libraries is uncommon - use common ``build`` params:
--libraries --include-dirs --library-dirs.

   >>> python setup.py build_ext --external --include-dirs /opt/zstd/usr/include --libraries zstd --library-dirs /opt/zstd/lib clean


Install from pypi
-----------------

   >>> # for Python 2.6+
   >>> pip install zstd
   >>> # or for Python 3.2+
   >>> pip3 install zstd

