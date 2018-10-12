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
# The feature of skipping tests was added to unittest in 2.7.
# If necessary, shim TestCase.skipTest and supply a SkipTest
# exception.  The skip decorators are not shimmed.

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

    LEGACY = False

    def setUp(self):
        if os.getenv("LEGACY"):
            self.LEGACY = True
