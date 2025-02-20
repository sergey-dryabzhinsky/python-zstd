#!/usr/bin/env python

import os
import sys

#debug
# print("\ncmdline: %r" % (sys.argv,))

import subprocess
import platform 

import setuptools
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

# bundled ZSTD version
VERSION = (1, 5, 6,)
VERSION_STR = ".".join([str(x) for x in VERSION])

###
# Ugly hacks, I know
#

SUP_LEGACY="ZSTD_LEGACY" in os.environ
if "--legacy" in sys.argv:
    # Support legacy output format functions
    SUP_LEGACY=True
    sys.argv.remove("--legacy")

SUP_WARNINGS="ZSTD_WARNINGS" in os.environ
if "--all--warnings" in sys.argv:
    # Support legacy output format functions
    SUP_WARNINGS=True
    sys.argv.remove("--all-warnings")

SUP_ASM="ZSTD_ASM" in os.environ
if "ZSTD_ASM" not in os.environ:
    SUP_ASM = True 
#a asm on by default
if "--libzstd-no-use-asm" in sys.argv:
    # Support assembler builtin optimization in lizstd
    SUP_ASM=False
    sys.argv.remove("--libzstd-no-use-asm")
DISABLE_ASM=1
if SUP_ASM:
     DISABLE_ASM=0

SUP_THREADS="ZSTD_THREADS" in os.environ 
if "ZSTD_THREADS" not in os.environ:
    SUP_THREADS = True
# threads on by default
if "--libzstd-no-threads" in sys.argv:
    # Disable support multithreading in lizstd
    SUP_THREADS=False
    sys.argv.remove("--libzstd-no-threads")
ENABLE_THREADS=0
if SUP_THREADS:
     ENABLE_THREADS=1

SUP_ASM_BMI2="ZSTD_ASM_BMI2" in os.environ
if "--libzstd-use-asm-bmi2" in sys.argv:
    # Support assembler builtin optimization in lizstd for new AMD CPU
    SUP_ASM_BMI2=True 
    sys.argv.remove("--libzstd-use-asm-bmi2")
ENABLE_ASM_BMI2=0
if SUP_ASM_BMI2:
     ENABLE_ASM_BMI2=1

SUP_TRACE="ZSTD_TRACE" in os.environ
if "--debug-trace" in sys.argv:
    # Support tracing for debug
    SUP_TRACE=True
    sys.argv.remove("--debug-trace")

BUILD_SMALL="ZSTD_SMALL" in os.environ
if "--small" in sys.argv:
    # Support tracing for debug
    BUILD_SMALL=True 
    sys.argv.remove("--small")
    
SUP_EXTERNAL="ZSTD_EXTERNAL" in os.environ
ext_libraries=[]
if "--external" in sys.argv:
    # You want use external Zstd library?
    SUP_EXTERNAL=True
    sys.argv.remove("--external")

pkgconf = "/usr/bin/pkg-config"
if "--libzstd-bundled" in sys.argv:
    # Do you want use external Zstd library?
    SUP_EXTERNAL=False
    sys.argv.remove("--libzstd-bundled")
    pkgconf = "/usr/bin/do-not-use-pkg-config"
    
#if SUP_EXTERNAL:
if platform.system() == "Linux" and "build_ext" in sys.argv or "build" in sys.argv or "bdist_wheel" in sys.argv:
    # You should add external library by option: --libraries zstd
    # And probably include paths by option: --include-dirs /usr/include/zstd
    # And probably library paths by option: --library-dirs /usr/lib/i386-linux-gnu
    # We need pkg-config here!
    if os.path.exists(pkgconf):
        #debug 
        #print("pkg-config exists")
        cmd = [pkgconf, "libzstd", "--modversion"]
        if sys.hexversion >= 0x03000000:
            VERSION_STR=b''
        else:
            VERSION_STR=""
        if sys.hexversion >= 0x02070000:
            try:
                VERSION_STR = subprocess.check_output(cmd).strip()
            except Exception as e:
                print("Error: %r" % e) 
                pass
        else:
            # Pure Python 2.6
            VERSION_STR = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0].strip()
        if sys.hexversion >= 0x03000000:
            # It's bytes in PY3
            VERSION_STR = VERSION_STR.decode()
        print("\nFound libzstd version %r" % VERSION_STR)
        if VERSION_STR and SUP_EXTERNAL:
            if VERSION_STR>="1.4.0":
                SUP_EXTERNAL=True
                if "--libraries" not in sys.argv:
                    # Add something default
                    ext_libraries=["zstd"]
            else:
                raise RuntimeError("Need zstd library verion >= 1.4.0")
            VERSION = tuple(int(v) for v in VERSION_STR.split("."))
    else:
        if SUP_EXTERNAL:
            # Require pkg config
            raise RuntimeError("Need pkg-config to find system libzstd.")
        print("\n Need pkg-config to find system libzstd. Or we try bundled one.")



# Package version, even external 
PKG_VERSION = VERSION
# Minor revision 
PKG_VERSION += ("4",)
PKG_VERSION_STR = ".".join([str(x) for x in PKG_VERSION])


if BUILD_SMALL:
   COPT = {
       'msvc': ['/O1', ],
       'mingw32': ['-Os',],
       'unix': ['-Os',],
       'clang': ['-Os',],
       'gcc': ['-Os',],
   }
else:
    COPT = {
       'msvc': ['/Ox', ],
       'mingw32': ['-O2',],
       'unix': ['-O2',],
       'clang': ['-O2',],
       'gcc': ['-O2',],
    }
###
# DVERSION - pass module version string
# DDYNAMIC_BMI2 - disable BMI2 amd64 asembler code - can't build it, use CFLAGS with -march= bdver4, znver1/2/3, native
# DZSTD_DISABLE_ASM=1 - disable ASM inlines


for comp in COPT:
    if comp == 'msvc':
        COPT[comp].extend([ '/DVERSION=%s' % PKG_VERSION_STR, '/DDYNAMIC_BMI2=%d' % ENABLE_ASM_BMI2, '/DZSTD_DISABLE_ASM=%d' % DISABLE_ASM ]),
    else:
        COPT[comp].extend([ '-DVERSION=%s' % PKG_VERSION_STR, '-DDYNAMIC_BMI2=%d' % ENABLE_ASM_BMI2, '-DZSTD_DISABLE_ASM=%d' % DISABLE_ASM ]),
   
        
if not SUP_EXTERNAL:
    for comp in COPT:
        if comp == 'msvc':
            COPT[comp].extend([ '/DZSTD_MULTITHREAD=%d' % ENABLE_THREADS,
                '/Izstd\\lib', '/Izstd\\lib\\common', '/Izstd\\lib\\compress', '/Izstd\\lib\\decompress',
            ])
        else:
            COPT[comp].extend([ '-DZSTD_MULTITHREAD=%d' % ENABLE_THREADS,
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

if SUP_WARNINGS:
    for comp in COPT:
        if comp == 'msvc':
            COPT[comp].extend(['/Wall', '/WX'])
        else:
            COPT[comp].extend(['-Wall', '-Wextra', '-Werror'])
            
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
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromName("tests.test_decompress"))
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromName("tests.test_version"))
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromName("tests.test_speed"))
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
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
    ]
)
