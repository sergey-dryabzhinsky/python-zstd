#!/usr/bin/env python

import sys

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

VERSION = (1, 0, 0)
VERSION_STR = ".".join([str(x) for x in VERSION])

# Minor versions
PKG_VERSION = VERSION + (99, 1,)
PKG_VERSION_STR = ".".join([str(x) for x in PKG_VERSION])

###
# Ugly hacks, I know
#

SUP_LEGACY=0
if "--legacy" in sys.argv:
    SUP_LEGACY=1
    sys.argv.remove("--legacy")

SUP_EXTERNAL=0
ext_libraries=[]
if "--external" in sys.argv:
    # You want use external Zstd library?
    SUP_EXTERNAL=1
    sys.argv.remove("--external")
    # You should add external library by option: --libraries zstd
    # And probably include paths by option: --include-dirs /usr/include/zstd
    # And probably library paths by option: --library-dirs /usr/lib/i386-linux-gnu
    if "--libraries" not in sys.argv:
        # Add something default
        ext_libraries=["zstd"]


COPT = {
    'msvc':     [ '/Ox', ],
    'mingw32':  [ '-O2', ],
    'unix':     [ '-O2', ],
    'clang':    [ '-O2', ],
    'gcc':      [ '-O2', ]
}

if not SUP_EXTERNAL:
    for comp in COPT:
        if comp == 'msvc':
            COPT[comp].extend([
                '/Izstd\\lib', '/Izstd\\lib\\common', '/Izstd\\lib\\compress', '/Izstd\\lib\\decompress',
                '/DVERSION=\"\\\"%s\\\"\"' % VERSION_STR,
            ])
        else:
            COPT[comp].extend([
                '-Izstd/lib', '-Izstd/lib/common', '-Izstd/lib/compress', '-Izstd/lib/decompress',
                '-DVERSION="%s"' % VERSION_STR,
            ])

if SUP_LEGACY:
    for comp in COPT:
        if comp == 'msvc':
            COPT[comp].extend(['/Izstd\\lib\\legacy', '/DZSTD_LEGACY_SUPPORT=1'])
        else:
            COPT[comp].extend(['-Izstd/lib/legacy', '-DZSTD_LEGACY_SUPPORT=1'])


class ZstdBuildExt( build_ext ):

    def build_extensions(self):
        c = self.compiler.compiler_type
        if c in COPT:
           for e in self.extensions:
               e.extra_compile_args = COPT[c]
        build_ext.build_extensions(self)

zstdFiles = []

if not SUP_EXTERNAL:

    for f in [
            'compress/zstd_compress.c', 'compress/fse_compress.c', 'compress/huf_compress.c', 'compress/zbuff_compress.c',
            'decompress/zstd_decompress.c', 'common/fse_decompress.c', 'decompress/huf_decompress.c', 'decompress/zbuff_decompress.c',
#            'dictBuilder/zdict.c', 'dictBuilder/divsufsort.c',
            'common/entropy_common.c', 'common/zstd_common.c', 'common/xxhash.c',
        ]:
        zstdFiles.append('zstd/lib/'+f)

    if SUP_LEGACY:
        for f in [
            'legacy/zstd_v01.c', 'legacy/zstd_v02.c', 'legacy/zstd_v03.c', 'legacy/zstd_v04.c', 'legacy/zstd_v05.c', 'legacy/zstd_v06.c', 'legacy/zstd_v07.c'
            ]:
            zstdFiles.append('zstd/lib/'+f)

zstdFiles.append('src/python-zstd.c')

tests="tests.generic"
if SUP_LEGACY:
    tests="tests.legacy"

setup(
    name='zstd',
    version=PKG_VERSION_STR,
    description="ZSTD Bindings for Python",
    long_description=open('README.rst', 'r').read(),
    author='Sergey Dryabzhinsky, Anton Stuk',
    author_email='sergey.dryabzhinsky@gmail.com',
    maintainer='Sergey Dryabzhinsky',
    maintainer_email='sergey.dryabzhinsky@gmail.com',
    url='https://github.com/sergey-dryabzhinsky/python-zstd',
    keywords='zstd, zstandard, compression',
    license='BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    ext_modules=[
        Extension('zstd', zstdFiles, libraries=ext_libraries)
    ],
    cmdclass = {'build_ext': ZstdBuildExt },
    test_suite=tests,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: POSIX',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
