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
VERSION = (1, 5, 7,)
VERSION_STR = ".".join([str(x) for x in VERSION])


# Package version, even external 
PKG_VERSION = VERSION
# Minor revision 
PKG_VERSION += ("1",)
PKG_VERSION_STR = ".".join([str(x) for x in PKG_VERSION])


def which(bin_exe):
    """
    Simulate shutil.which for python 2.7,
    which available only since python 3.3.
    Search executable in common paths.

    @return: False or full path to executable 
    @rtype: str|bool
    """
    # support Linux / POSIX here? Or maybe windows?
    paths = ["/usr/local/bin", "/usr/local/sbin", "/bin", "/sbin", "/usr/bin", "/usr/sbin"]
    if "PATH" in os.environ:
        paths = os.environ["PATH"].split(":")
    for p in paths:
        full_path = os.path.join(p, bin_exe)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path
    return False
###
# Ugly hacks, I know
#

SUP_LEGACY="ZSTD_LEGACY" in os.environ
if "--legacy" in sys.argv:
    # Support legacy output format functions
    if SUP_LEGACY:
        if os.environ[ZSTD_LEGACY]=='0':
            SUP_LEGACY=False
        else:
            SUP_LEGACY=True
    sys.argv.remove("--legacy")

SUP_WARNINGS="ZSTD_WARNINGS" in os.environ
if SUP_WARNINGS:
    if os.environ["ZSTD_WARNINGS"]=='0':
        SUP_WARNINS=False
    else:
        SUP_WARNINGS=True
if "--all-warnings" in sys.argv:
    SUP_WARNINGS=True
    sys.argv.remove("--all-warnings")

SUP_WERROR="ZSTD_WERRORS" in os.environ
if SUP_WERROR:
    if os.environ["ZSTD_WERRORS"]=='0':
        SUP_WERROR=False
    else:
        SUP_WERROR=True
if "--all-warnings-errors" in sys.argv:
    # Support legacy output format functions
    SUP_WERROR=True
    sys.argv.remove("--all-warnings-errors")
    
SUP_ASM="ZSTD_ASM" in os.environ
if "ZSTD_ASM" not in os.environ:
    SUP_ASM = False
#a asm off by default
if "--libzstd-use-asm" in sys.argv:
    # Support assembler builtin optimization in lizstd
    SUP_ASM=True
    sys.argv.remove("--libzstd-use-asm")
DISABLE_ASM=0
if not SUP_ASM:
     DISABLE_ASM=1

SUP_THREADS="ZSTD_THREADS" in os.environ 
if "ZSTD_THREADS" not in os.environ:
    SUP_THREADS = True
else:
    if os.environ['ZSTD_THREADS']=='0':
        SUP_THREADS = False
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
BUILD_SPEED0="ZSTD_SPEED0" in os.environ
if "--speed0" in sys.argv:
    # speed or size choose only one
    if BUILD_SPEED0:
        if os.environ["ZSTD_SPEED0"]=='0':
            BUILD_SPEED0=False
    BUILD_SPEED0=True
    BUILD_SMALL=False
    sys.argv.remove("--speed0")
else:
    BUILD_SPEED0=False

BUILD_SPEED1="ZSTD_SPEED1" in os.environ
if "--speed1" in sys.argv:
    if BUILD_SPEED1:
        if os.environ["ZSTD_SPEED1"]=='0':
            BUILD_SPEED1=False
    # speed or size choose only one
    BUILD_SPEED1=True
    BUILD_SMALL=False
    sys.argv.remove("--speed1")
else:
    BUILD_SPEED1=False

BUILD_SPEED2="ZSTD_SPEED2" in os.environ
if "--speed2" in sys.argv:
    if BUILD_SPEED2:
        if os.environ["ZSTD_SPEED2"]=='0':
            BUILD_SPEED2=False
    # speed or size choose only one
    BUILD_SPEED2=True
    BUILD_SMALL=False
    sys.argv.remove("--speed2")
else:
    BUILD_SPEED2=False

BUILD_SPEED3="ZSTD_SPEED3" in os.environ
if "--speed3" in sys.argv:
    # speed or size choose only one
    BUILD_SPEED3=True
    BUILD_SMALL=False
    sys.argv.remove("--speed3")
else:
    BUILD_SPEED3=True
if BUILD_SPEED3:
    if os.environ.get("ZSTD_SPEED3")=='0':
        BUILD_SPEED3=False

BUILD_SPEEDMAX="ZSTD_SPEEDMAX" in os.environ
if "--speed-max" in sys.argv:
    # speed or size choose only one
    BUILD_SPEED3=True
    BUILD_SPEEDMAX=True 
    BUILD_SMALL=False
    sys.argv.remove("--speed-max")

BUILD_SMALL="ZSTD_SMALL" in os.environ
if "--small" in sys.argv:
    if BUILD_SMALL:
        if os.environ["ZSTD_SMALL"]=='0':
            BUILD_SMALL=False
    BUILD_SMALL=True
    BUILD_SPEED3=False
    sys.argv.remove("--small")
else:
    BUILD_SMALL=False

SUP_EXTERNAL="ZSTD_EXTERNAL" in os.environ
ext_libraries=[]
if "--external" in sys.argv:
    # You want use external Zstd library?
    SUP_EXTERNAL=True
    sys.argv.remove("--external")

SUP_DEBUG="ZSTD_DEBUG" in os.environ
if SUP_DEBUG:
    if os.environ["ZSTD_DEBUG"]=='0':
        SUP_DEBUG=False
ext_libraries=[]
if "--debug" in sys.argv:
    SUP_DEBUG=True
    sys.argv.remove("--debug")

SUP_DEBUG_NOTICE="ZSTD_DEBUG_NOTICE" in os.environ
if SUP_DEBUG_NOTICE:
    SUP_DEBUG=True
    if os.environ["ZSTD_DEBUG_NOTICE"]=='0':
        SUP_DEBUG_NOTICE=False
ext_libraries=[]
if "--debug-notice" in sys.argv:
    SUP_DEBUG_NOTICE=True
    SUP_DEBUG=True
    sys.argv.remove("--debug-notice")

SUP_DEBUG_INFO="ZSTD_DEBUG_INFO" in os.environ
if SUP_DEBUG_INFO:
    SUP_DEBUG=True
    if os.environ["ZSTD_DEBUG_INFO"]=='0':
        SUP_DEBUG_INFO=False
ext_libraries=[]
if "--debug-info" in sys.argv:
    SUP_DEBUG_INFO=True
    SUP_DEBUG=True
    sys.argv.remove("--debug-info")

SUP_DEBUG_ERROR="ZSTD_DEBUG_ERROR" in os.environ
if SUP_DEBUG_ERROR:
    SUP_DEBUG=True
    if os.environ["ZSTD_DEBUG_ERROR"]=='0':
        SUP_DEBUG_ERROR=False
ext_libraries=[]
if "--debug-error" in sys.argv:
    SUP_DEBUG_ERROR=True
    SUP_DEBUG=True
    sys.argv.remove("--debug-error")

#Some python builds need to disable LTO by force
BUILD_NO_LTO="ZSTD_BUILD_NO_LTO" in os.environ
if BUILD_NO_LTO:
    if os.environ["ZSTD_BUILD_NO_LTO"]=='0':
        BUILD_NO_LTO=False
if "--force-no-lto" in sys.argv:
    BUILD_NO_LTO=True
    sys.argv.remove("--force-no-lto")
else:
    BUILD_NO_LTO=True

BUILD_STRIP="ZSTD_BUILD_STRIP" in os.environ
if BUILD_STRIP:
    if os.environ["ZSTD_BUILD_STRIP"]=='0':
        BUILD_STRIP=False
if "--force-strip" in sys.argv:
    BUILD_STRIP=True
    sys.argv.remove("--force-strip")
else:
    BUILD_STRIP=True
    
pkgconf = which("pkg-config")
if "--libzstd-bundled" in sys.argv:
    # Do you want use external Zstd library?
    SUP_EXTERNAL=False
    sys.argv.remove("--libzstd-bundled")
    pkgconf = False

#if SUP_EXTERNAL:
if platform.system() == "Linux" and "build_ext" in sys.argv or "build" in sys.argv or "bdist_wheel" in sys.argv:
    # You should add external library by option: --libraries zstd
    # And probably include paths by option: --include-dirs /usr/include/zstd
    # And probably library paths by option: --library-dirs /usr/lib/i386-linux-gnu
    # We need pkg-config here!
    if pkgconf is not False:
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
        #debug
        if SUP_DEBUG:
            print("\nFound libzstd version %r" % VERSION_STR)
        if VERSION_STR and SUP_EXTERNAL:
            if VERSION_STR>="1.4.0":
                SUP_EXTERNAL=True
                if "--libraries" not in sys.argv:
                    # Add something default
                    ext_libraries=["zstd"]
            else:
                raise RuntimeError("Need zstd library verion >= 1.4.0")
            #VERSION = tuple(int(v) for v in VERSION_STR.split("."))
    else:
        if SUP_EXTERNAL:
            # Require pkg config
            raise RuntimeError("Need pkg-config to find system libzstd.")
        print("\n Need pkg-config to find system libzstd. Or we try bundled one.")


# default standard optimization
COPT = {
    'msvc': ['/O2', ],
    'mingw32': ['-O2',],
    'unix': ['-O2',],
    'clang': ['-O2',],
    'gcc': ['-O2',],
}
if BUILD_SMALL:
   COPT = {
       'msvc': ['/O1', ],
       'mingw32': ['-Os',],
       'unix': ['-Os',],
       'clang': ['-Os',],
       'gcc': ['-Os',],
   }

# not small, but speed?
if BUILD_SPEED0:
    COPT = {
        'msvc': ['/O0', ],
        'mingw32': ['-O0',],
        'unix': ['-O0',],
        'clang': ['-O0',],
        'gcc': ['-O0',],
    }
if BUILD_SPEED1:
    COPT = {
        'msvc': ['/O1', ],
        'mingw32': ['-O1',],
        'unix': ['-O1',],
        'clang': ['-O1',],
        'gcc': ['-O1',],
    }
if BUILD_SPEED2:
    COPT = {
        'msvc': ['/O2', ],
        'mingw32': ['-O3',],
        'unix': ['-O3',],
        'clang': ['-O3',],
        'gcc': ['-O3',],
    }
if BUILD_SPEED3:
    COPT = {
        'msvc': ['/O3', ],
        'mingw32': ['-O3',],
        'unix': ['-O3',],
        'clang': ['-O3',],
        'gcc': ['-O3',],
    }
###
# DVERSION - pass module version string
# DDYNAMIC_BMI2 - disable BMI2 amd64 asembler code - can't build it, use CFLAGS with -march= bdver4, znver1/2/3, native
# DZSTD_DISABLE_ASM=1 - disable ASM inlines


for comp in COPT:
    if comp == 'msvc':
        COPT[comp].extend([ '/DMOD_VERSION=%s' % PKG_VERSION_STR, '/DDYNAMIC_BMI2=%d' % ENABLE_ASM_BMI2, '/DZSTD_DISABLE_ASM=%d' % DISABLE_ASM ]),
    else:
        COPT[comp].extend([ '-DMOD_VERSION=%s' % PKG_VERSION_STR, '-DDYNAMIC_BMI2=%d' % ENABLE_ASM_BMI2, '-DZSTD_DISABLE_ASM=%d' % DISABLE_ASM ]),


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

if SUP_DEBUG:
    for comp in COPT:
        if comp == 'msvc':
            COPT[comp].extend([ '/DZSTD_DEBUG=1','-g',
            ])
        else:
            COPT[comp].extend([ '-DZSTD_DEBUG=1','-g',
            ])

if BUILD_NO_LTO:
    for comp in COPT:
        if comp == 'msvc':
            pass
        else:
            COPT[comp].extend([ '-fno-lto',
            ])

if SUP_DEBUG_NOTICE:
    for comp in COPT:
        if comp == 'msvc':
            COPT[comp].extend([ '/DZSTD_DEBUG_NOTICE=1',
            ])
        else:
            COPT[comp].extend([ '-DZSTD_DEBUG_NOTICE=1',
            ])

if SUP_DEBUG_INFO:
    for comp in COPT:
        if comp == 'msvc':
            COPT[comp].extend([ '/DZSTD_DEBUG_INFO=1',
            ])
        else:
            COPT[comp].extend([ '-DZSTD_DEBUG_INFO=1',
            ])

if SUP_DEBUG_ERROR:
    for comp in COPT:
        if comp == 'msvc':
            COPT[comp].extend([ '/DZSTD_DEBUG_ERROR=1',
            ])
        else:
            COPT[comp].extend([ '-DZSTD_DEBUG_ERROR=1',
            ])

if BUILD_SPEEDMAX:
    for comp in COPT:
        if comp == 'msvc':
            COPT[comp].extend([ ''
            ])
        else:
            COPT[comp].extend([ '-march=native',
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
            COPT[comp].extend(['/Wall',])
        else:
            COPT[comp].extend(['-Wall', '-Wextra', 
#'-Wpedantic'
])

if SUP_WERROR:
    for comp in COPT:
        if comp == 'msvc':
            COPT[comp].extend(['//WX'])
        else:
            COPT[comp].extend(['-Werror'])

if BUILD_STRIP:
    for comp in COPT:
        if comp == 'msvc':
            pass
        else:
            COPT[comp].extend(['-Wl,-s'])

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

# protect from python packaged flags that prevent from exporting symbols
for comp in COPT:
    if comp == 'msvc':
        pass
    else:
        COPT[comp].extend(['-std=c99','-fvisibility=default'])

# disable some msvc warnings
for comp in COPT:
    if comp == 'msvc':
        COPT[comp].extend(['/wd4996'])


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
            'compress/zstd_preSplit.c',
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

zstdFiles.append('src/debug.c')
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
if "test" in sys.argv:
    from setuptools.version import __version__ as version
    print("setuptools version %r" % version)
    if version < '72.0':
        test_func_name = "tests"

f=open('README.rst', 'r')
ld=f.read()
f.close()

setup(
    name='zstd',
    version=PKG_VERSION_STR,
    description="ZSTD Bindings for Python",
    long_description=ld,
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
#        'License :: OSI Approved :: BSD License',
        
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
