# Tests

import os

from tests.base import BaseTestZSTD, raise_skip

class TestZSTD(BaseTestZSTD):

    def setUp(self):
        self.VERSION = os.getenv("VERSION")
        self.PKG_VERSION = os.getenv("PKG_VERSION")

    def test_module_version(self):
        BaseTestZSTD.helper_version(self)

    def test_library_version(self):
        BaseTestZSTD.helper_zstd_version(self)

if __name__ == '__main__':
    unittest.main()
