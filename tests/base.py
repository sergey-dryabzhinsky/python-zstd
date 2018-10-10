# -*- coding: utf-8 -*-

import logging
import os
import sys
import unittest

import zstd

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ZSTD")
log.info("Python version: %s" % sys.version)

###
# Compatibility headache: The feature of skipping tests was added to
# unittest in 2.7.  If necessary, provide a SkipTest exception and a
# TestZSTD class that shims TestCase.skipTest().  The skip decorators
# are not shimmed.

if hasattr(unittest, "SkipTest"):
    SkipTest = unittest.SkipTest
    BaseTestCase = unittest.TestCase

else:
    class SkipTest(Exception):
        pass

    class BaseTestCase(unittest.TestCase):
        def skipTest(reason):
            raise SkipTest(reason)

        # super().run() needs to do work before and after calling the
        # actual test method, whether or not that method terminates by
        # raising SkipTest.  So we must arrange to inject a wrapper
        # around the test method itself.
        def run(self, result=None):
            try:
                self._realTestMethodName = self._testMethodName
                self._testMethodName = "shimTestMethod"
                unittest.TestCase.run(self, result)
            finally:
                self._testMethodName = self._realTestMethodName

        def shimTestMethod(self):
            try:
                realTestMethod = getattr(self, self._realTestMethodName)
                return realTestMethod()
            except SkipTest as e:
                log.info("%s: test skipped: %s"
                         % (self._realTestMethodName, str(e)))

###
# zstd-specific TestCase subclass

class BaseTestZSTD(BaseTestCase):

    ZSTD_EXTERNAL = False
    LEGACY = False
    PYZSTD_LEGACY = False
    VERSION = ""
    VERSION_INT = 0
    VERSION_INT_MIN = 1 * 100*100 + 0 * 100 + 0
    PKG_VERSION = ""

    def setUp(self):
        if os.getenv("LEGACY"):
            self.LEGACY = True
        if os.getenv("PYZSTD_LEGACY"):
            self.PYZSTD_LEGACY = True
        if os.getenv("ZSTD_EXTERNAL"):
            self.ZSTD_EXTERNAL = True

        self.VERSION = os.getenv("VERSION")
        self.PKG_VERSION = os.getenv("PKG_VERSION")
        v = [int(n) for n in self.VERSION.split(".")]
        v = sorted(v, reverse=True)
        self.VERSION_INT = 0
        i = 0
        for n in v:
            self.VERSION_INT += n * 100**i
            i += 1
