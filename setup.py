#!/usr/bin/env python

import sys

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

VERSION = (1, 0, 0)
VERSION_STR = ".".join([str(x) for x in VERSION])


SUP_LEGACY=0
if "--legacy" in sys.argv:
    SUP_LEGACY=1
    sys.argv.remove("--legacy")


COPT = {
    'msvc': [
                '/Ox',
                '/Izstd\\lib', '/Izstd\\lib\\common', '/Izstd\\lib\\compress', '/Izstd\\lib\\decompress',
                '/DVERSION=\"\\\"%s\\\"\"' % VERSION_STR,
            ],
    'mingw32':  [
                    '-O2',
                    '-Izstd/lib', '-Izstd/lib/common', '-Izstd/lib/compress', '-Izstd/lib/decompress',
                    '-DVERSION="%s"' % VERSION_STR,
                ],
    'unix': [
                '-O2',
                '-Izstd/lib', '-Izstd/lib/common', '-Izstd/lib/compress', '-Izstd/lib/decompress',
                '-DVERSION="%s"' % VERSION_STR,
            ],
    'clang':    [
                    '-O2',
                    '-Izstd/lib', '-Izstd/lib/common', '-Izstd/lib/compress', '-Izstd/lib/decompress',
                    '-DVERSION="%s"' % VERSION_STR,
                ],
    'gcc':  [
                '-O2',
                '-Izstd/lib', '-Izstd/lib/common', '-Izstd/lib/compress', '-Izstd/lib/decompress',
                '-DVERSION="%s"' % VERSION_STR,
            ]
}

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
for f in [
        'compress/zstd_compress.c', 'compress/fse_compress.c', 'compress/huf_compress.c', 'compress/zbuff_compress.c',
        'decompress/zstd_decompress.c', 'common/fse_decompress.c', 'decompress/huf_decompress.c', 'decompress/zbuff_decompress.c',
#        'dictBuilder/zdict.c', 'dictBuilder/divsufsort.c',
        'common/entropy_common.c', 'common/zstd_common.c', 'common/xxhash.c',
    ]:
    zstdFiles.append('zstd/lib/'+f)

if SUP_LEGACY:
    for f in [
        'legacy/zstd_v01.c', 'legacy/zstd_v02.c', 'legacy/zstd_v03.c', 'legacy/zstd_v04.c', 'legacy/zstd_v05.c', 'legacy/zstd_v06.c', 'legacy/zstd_v07.c'
        ]:
        zstdFiles.append('zstd/lib/'+f)


zstdFiles.append('src/python-zstd.c')

setup(
    name='zstd',
    version=VERSION_STR,
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
        Extension('zstd', zstdFiles)
    ],
    cmdclass = {'build_ext': ZstdBuildExt },
    test_suite="tests",
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
