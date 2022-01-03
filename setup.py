#!/usr/bin/env python

import os
import sys
import subprocess

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

# ZSTD version
VERSION = (1, 5, 1,)
VERSION_STR = ".".join([str(x) for x in VERSION])

# Package version
PKG_VERSION = VERSION
# Minor versions
PKG_VERSION += ("0",)
PKG_VERSION_STR = ".".join([str(x) for x in PKG_VERSION])

###
# Ugly hacks, I know
#

SUP_LEGACY=0
if "--legacy" in sys.argv:
    # Support legacy output format functions
    SUP_LEGACY=1
    sys.argv.remove("--legacy")

SUP_TRACE=0
if "--debug-trace" in sys.argv:
    # Support tracing for debug
    SUP_TRACE=1
    sys.argv.remove("--debug-trace")

SUP_EXTERNAL=0
ext_libraries=[]
if "--external" in sys.argv:
    # You want use external Zstd library?
    SUP_EXTERNAL=1
    sys.argv.remove("--external")
    # You should add external library by option: --libraries zstd
    # And probably include paths by option: --include-dirs /usr/include/zstd
    # And probably library paths by option: --library-dirs /usr/lib/i386-linux-gnu
    # Wee need pkg-config here!
    pkgconf = "/usr/bin/pkg-config"
    if os.path.exists(pkgconf):
        cmd = [pkgconf, "libzstd", "--modversion"]
        if sys.hexversion >= 0x02070000:
            VERSION_STR = subprocess.check_output(cmd)
        else:
            # Pure Python 2.6
            VERSION_STR = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
        if sys.hexversion >= 0x03000000:
            # It's bytes in PY3
            VERSION_STR = VERSION_STR.decode()
        VERSION = tuple(int(v) for v in VERSION_STR.split("."))
    if "--libraries" not in sys.argv:
        # Add something default
        ext_libraries=["zstd"]


###
# DVERSION - pass module version string
# DDYNAMIC_BMI2 - disable BMI2 amd64 asembler code - can't build it, use CFLAGS with -march= bdver4, znver1/2/3, native
#
COPT = {
    'msvc':     [ '/Ox', '/DVERSION=%s' % PKG_VERSION_STR, '/DDYNAMIC_BMI2=0' ],
    'mingw32':  [ '-O2', '-DVERSION=%s' % PKG_VERSION_STR, '-DDYNAMIC_BMI2=0' ],
    'unix':     [ '-O2', '-DVERSION=%s' % PKG_VERSION_STR, '-DDYNAMIC_BMI2=0' ],
    'clang':    [ '-O2', '-DVERSION=%s' % PKG_VERSION_STR, '-DDYNAMIC_BMI2=0' ],
    'gcc':      [ '-O2', '-DVERSION=%s' % PKG_VERSION_STR, '-DDYNAMIC_BMI2=0' ]
}

if not SUP_EXTERNAL:
    for comp in COPT:
        if comp == 'msvc':
            COPT[comp].extend([ '/DZSTD_MULTITHREAD=1',
                '/Izstd\\lib', '/Izstd\\lib\\common', '/Izstd\\lib\\compress', '/Izstd\\lib\\decompress',
            ])
        else:
            COPT[comp].extend([ '-DZSTD_MULTITHREAD=1',
                '-Izstd/lib', '-Izstd/lib/common', '-Izstd/lib/compress', '-Izstd/lib/decompress',
            ])
else:
    for comp in COPT:
        if comp == 'msvc':
            COPT[comp].extend([ '/DLIBZSTD_EXTERNAL=1'
            ])
        else:
            COPT[comp].extend([ '-DLIBZSTD_EXTERNAL=1',
            ])

if SUP_LEGACY:
    for comp in COPT:
        if comp == 'msvc':
            COPT[comp].extend(['/Izstd\\lib\\legacy', '/DZSTD_LEGACY_SUPPORT=1'])
        else:
            COPT[comp].extend(['-Izstd/lib/legacy', '-DZSTD_LEGACY_SUPPORT=1'])

# Force traceing support or disable
if SUP_TRACE:
    for comp in COPT:
        if comp == 'msvc':
            COPT[comp].extend(['/DZSTD_TRACE=1'])
        else:
            COPT[comp].extend(['-DZSTD_TRACE=1'])
else:
    for comp in COPT:
        if comp == 'msvc':
            COPT[comp].extend(['/DZSTD_TRACE=0'])
        else:
            COPT[comp].extend(['-DZSTD_TRACE=0'])


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
            'compress/zstd_compress.c',
            'compress/zstd_compress_literals.c',
            'compress/zstd_compress_sequences.c',
            'compress/zstd_compress_superblock.c',
            'compress/zstdmt_compress.c',
            'compress/zstd_fast.c',
            'compress/zstd_double_fast.c',
            'compress/zstd_lazy.c',
            'compress/zstd_opt.c',
            'compress/zstd_ldm.c',
            'compress/fse_compress.c',
            'compress/huf_compress.c',
            'compress/hist.c',

            'common/fse_decompress.c',
            'decompress/zstd_decompress.c',
            'decompress/zstd_decompress_block.c',
            'decompress/zstd_ddict.c',
            'decompress/huf_decompress.c',

            'common/entropy_common.c',
            'common/zstd_common.c',
            'common/xxhash.c',
            'common/error_private.c',
            'common/pool.c',
            'common/threading.c',
        ]:
        zstdFiles.append('zstd/lib/'+f)

    if SUP_LEGACY:
        for f in [
            'legacy/zstd_v01.c', 'legacy/zstd_v02.c', 'legacy/zstd_v03.c', 'legacy/zstd_v04.c', 'legacy/zstd_v05.c', 'legacy/zstd_v06.c', 'legacy/zstd_v07.c'
            ]:
            zstdFiles.append('zstd/lib/'+f)

zstdFiles.append('src/util.c')
zstdFiles.append('src/python-zstd.c')


# Another dirty hack
def my_test_suite():
    import unittest

    os.environ["VERSION"] = VERSION_STR
    os.environ["PKG_VERSION"] = PKG_VERSION_STR

    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromName("tests.test_compress"))
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromName("tests.test_version"))
    return test_suite

test_func_name = "setup.my_test_suite"

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
    keywords=['zstd', 'zstandard', 'compression'],
    license='BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    ext_modules=[
        Extension('zstd', zstdFiles, libraries=ext_libraries)
    ],
    cmdclass = {'build_ext': ZstdBuildExt },
    test_suite=test_func_name,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: POSIX',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ]
)
