# Tests

import os

from tests.base import BaseTestZSTD, log

class TestZSTD(BaseTestZSTD):

    def setUp(self):
        if os.getenv("ZSTD_EXTERNAL"):
            self.ZSTD_EXTERNAL = True
        self.VERSION = os.getenv("VERSION")
        self.PKG_VERSION = os.getenv("PKG_VERSION")
        log.info("VERSION=%r" % self.VERSION)
        log.info("PKG_VERSION=%r" % self.PKG_VERSION)
        v = [int(n) for n in reversed(self.VERSION.split("."))]
        log.info("v=%r" % (v,))
        self.VERSION_INT = 0
        i = 0
        for n in v:
            self.VERSION_INT += n * 100**i
            i += 1
        log.info("VERSION_INT=%r" % self.VERSION_INT)

    def test_module_version(self):
        BaseTestZSTD.helper_version(self)

    def test_library_version(self):
        BaseTestZSTD.helper_zstd_version(self)

    def test_library_version_number(self):
        BaseTestZSTD.helper_zstd_version_number(self)

if __name__ == '__main__':
    unittest.main()
