#!/usr/bin/env python

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

VERSION = (0, 3, 6)
VERSION_STR = ".".join([str(x) for x in VERSION])

COPT =  {'msvc': ['/Ox', '/Izstd\\lib', '/Izstd\\lib\\legacy', '/DVERSION=\"\\\"%s\\\"\"' % VERSION_STR],
     'mingw32' : ['-O3', '-Izstd/lib', '-Izstd/lib/legacy', '-DVERSION="%s"' % VERSION_STR],
     'unix' : ['-O3', '-Izstd/lib', '-Izstd/lib/legacy', '-DVERSION="%s"' % VERSION_STR],
     'clang' : ['-O3', '-Izstd/lib', '-Izstd/lib/legacy', '-DVERSION="%s"' % VERSION_STR],
     'gcc' : ['-O3', '-Izstd/lib', '-Izstd/lib/legacy', '-DVERSION="%s"' % VERSION_STR]}

class build_ext_subclass( build_ext ):
    def build_extensions(self):
        c = self.compiler.compiler_type
        if c in COPT:
           for e in self.extensions:
               e.extra_compile_args = COPT[c]
        build_ext.build_extensions(self)

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
        Extension('zstd', [
            'zstd/lib/huff0.c',
            'zstd/lib/fse.c',
            'zstd/lib/legacy/zstd_v01.c',
            'zstd/lib/legacy/zstd_v02.c',
            'zstd/lib/zstd.c',
            'zstd/lib/zstdhc.c',
            'src/python-zstd.c'
        ])
    ],
    cmdclass = {'build_ext': build_ext_subclass },
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
