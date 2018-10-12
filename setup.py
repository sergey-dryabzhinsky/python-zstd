#!/usr/bin/env python

import os
import shlex
import sys
import subprocess

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext as cmd_build_ext
from distutils.command.clean import clean as cmd_clean
from distutils.sysconfig import get_config_var

###
# Version policy: The first three elements of the package version will
# always match the version of the bundled libzstd.  The fourth element
# counts updates to the package in between updates to libzstd.
#
with open("PKG-INFO", "rt") as fp:
    for line in fp:
        k, _, v = line.strip().partition(": ")
        if k == "Version":
            PKG_VERSION_STR = v.strip()
            break
    else:
        sys.stderr.write("setup.py: error: version number not found "
                         "in PKG-INFO")
        sys.exit(1)

###
# Command line options
#
SUP_LEGACY = 0
SUP_EXTERNAL = 0

# The environment variables ensure that if setup() recursively invokes
# this setup.py in a subprocess, it gets the same settings.

# Support legacy versions of the compressed file format: both
# those produced by libzstd 0.7.x and older, and those produced
# by versions of this package prior to 1.0.0.99.1.
if "--legacy" in sys.argv:
    sys.argv.remove("--legacy")
    os.environ["PYZSTD_LEGACY"] = "1"
    SUP_LEGACY = 1
elif os.environ.get("PYZSTD_LEGACY", "0") == "1":
    SUP_LEGACY = 1

# Use an externally supplied copy of libzstd, instead of the bundled one.
if "--external" in sys.argv:
    sys.argv.remove("--external")
    os.environ["PYZSTD_EXTERNAL"] = "1"
    SUP_EXTERNAL = 1
elif os.environ.get("PYZSTD_EXTERNAL", "0") == "1":
    SUP_EXTERNAL = 1

if SUP_LEGACY and SUP_EXTERNAL:
    # We have to compile libzstd specially to get legacy format
    # support, so we can't use an external libzstd in that case.
    sys.stderr.write(
        "setup.py: error: legacy file formats are not supported with "
        "external libzstd\n")
    sys.exit(1)

ext_defines = [("PKG_VERSION_STR", '"' + PKG_VERSION_STR + '"')]
ext_include_dirs = []
ext_cflags = []
ext_libraries = []
ext_library_dirs = []
ext_ldflags = []

if SUP_EXTERNAL:
    if "--libraries" in sys.argv:
        # If --libraries was set by the user, assume they have taken
        # full responsibility for telling setup() where to find the external
        # libzstd.
        pass
    else:
        # Let's see if pkg-config will help us out.
        try:
            libs = subprocess.check_output(
                ["pkg-config", "libzstd", "--libs"])
            if libs:
                if not isinstance(libs, str):
                    libs = libs.decode(sys.getdefaultencoding())
                for lib in shlex.split(libs):
                    if lib[:2] == "-l":
                        ext_libraries.append(lib[2:])
                    elif lib[:3].lower() == "lib":
                        ext_libraries.append(lib)
                    elif lib[:2] in ('-L', '/L'):
                        ext_library_dirs.append(lib[:2])
                    else:
                        ext_ldflags.append(lib)

            cflags = subprocess.check_output(
                ["pkg-config", "libzstd", "--cflags"])
            if cflags:
                if not isinstance(cflags, str):
                    cflags = cflags.decode(sys.getdefaultencoding())
                for cflag in shlex.split(cflags):
                    if cflag[:2] == "-D" or cflag[:2] == "/D":
                        k, _, v = cflag[2:].partition('=')
                        if not v: v = "1"
                        ext_defines.append((k, v))
                    else:
                        ext_cflags.append(cflag)


        except CalledProcessError:
            # pkg-config is not available or does not know about libzstd.
            # Assume we don't need to do anything special.
            pass

        # If we still don't know the name of the external libzstd, guess.
        if not ext_libraries:
            ext_libraries.append("zstd")


    zstd_build_ext = cmd_build_ext
    zstd_clean = cmd_clean

else: # not SUP_EXTERNAL
    ext_libraries.append("zstd")
    ext_library_dirs.append("libzstd/lib")
    ext_include_dirs.append("libzstd/lib")
    if SUP_LEGACY:
        ext_defines.append(("ZSTD_LEGACY_SUPPORT", "1"))

    # Override build_ext.build_extensions to run 'make' in the libzstd
    # subdirectory first.
    class zstd_build_ext(cmd_build_ext):
        def build_extensions(self, *args, **kwargs):
            makecmd = ["make"]

            # Parallelism is supported by 'build_ext' since 3.5.
            # os.cpu_count() was added in 3.4.
            try:
                parallel = self.parallel
                if parallel is True:
                    parallel = os.cpu_count()
                if parallel is None or parallel < 1:
                    parallel = 1
            except AttributeError:
                parallel = 1

            if parallel > 1:
                makecmd.append("-j%d" % parallel)

            makecmd.extend([
                "-C", "libzstd/lib", "libzstd.a",
                "DEBUGFLAGS=",
                "MOREFLAGS=" + (get_config_var("CCSHARED") or ""),
                "ZSTD_LEGACY_SUPPORT=%d" % SUP_LEGACY,
                "ZSTD_LIB_DEPRECATED=0",
                "ZSTD_LIB_DICTBUILDER=0",
            ])

            subprocess.check_call(makecmd)
            cmd_build_ext.build_extensions(self, *args, **kwargs)

    # Similarly, on 'clean' run 'make clean' in the libzstd subdirectory.
    class zstd_clean(cmd_clean):
        def run(self):
            cmd_clean.run(self)
            subprocess.check_call([
                "make", "-C", "libzstd/lib", "clean"
            ])

# unittest.TestLoader.discover was added in 2.7.
def my_test_suite():
    import unittest
    import glob
    return unittest.defaultTestLoader.loadTestsFromNames(sorted(
        test[:-3].replace("/", ".")
        for test in glob.glob("tests/test_*.py")
    ))

if __name__ == '__main__':
    setup(
        name="zstd",
        version=PKG_VERSION_STR,
        description="ZSTD Bindings for Python",
        long_description=open("README.rst", "r").read(),
        author="Sergey Dryabzhinsky, Anton Stuk",
        author_email="sergey.dryabzhinsky@gmail.com",
        maintainer="Sergey Dryabzhinsky",
        maintainer_email="sergey.dryabzhinsky@gmail.com",
        url="https://github.com/sergey-dryabzhinsky/python-zstd",
        keywords=["zstd", "zstandard", "compression"],
        license="BSD",
        packages=find_packages(exclude="tests"),
        ext_modules=[
            Extension("zstd._zstd",
                      sources=["zstd/_zstd.c"],
                      define_macros=ext_defines,
                      include_dirs=ext_include_dirs,
                      extra_compile_args=ext_cflags,
                      libraries=ext_libraries,
                      library_dirs=ext_library_dirs,
                      extra_link_args=ext_ldflags
            )
        ],
        cmdclass = {
            "build_ext": zstd_build_ext,
            "clean": zstd_clean,
        },
        test_suite="setup.my_test_suite",
        classifiers=[
            "License :: OSI Approved :: BSD License",
            "Intended Audience :: Developers",
            "Development Status :: 5 - Production/Stable",
            "Operating System :: POSIX",
            "Programming Language :: C",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.2",
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
        ]
    )
