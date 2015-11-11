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

It is provided as a BSD-license package, hosted on [Github https://github.com/Cyan4973/zstd].

Build from source
-----------------

   >>> git clone https://github.com/sergey-dryabzhinsky/python-zstd
   >>> git submodule update --init
   >>> apt-get install python-dev python3-dev python-setuptools python3-setuptools
   >>> python setup.py build; python setup.py clean
   >>> python3 setup.py build; python3 setup.py clean
