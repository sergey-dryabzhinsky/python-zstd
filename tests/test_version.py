# Tests

import os
import zstd

from tests.base import BaseTestZSTD

class TestVersions(BaseTestZSTD):

    def test_module_version(self):
        self.assertEqual(self.PKG_VERSION, zstd.version())

    def test_library_version(self):
        if self.ZSTD_EXTERNAL:
            self.skipTest("PyZstd was build with external version of "
                          "ZSTD library (%s). It can be any version. Almost."
                          % zstd.library_version())

        self.assertEqual(self.VERSION, zstd.library_version())

    def test_library_version_number(self):
        if self.ZSTD_EXTERNAL:
            # Python 2.6 unittest missing assertLessEqual
            self.assertFalse(self.VERSION_INT_MIN >
                             zstd.library_version_number(),
                             msg="PyZstd %s require external library "
                             "version >= 1.0.0!" % zstd.version())
        else:
            self.assertEqual(self.VERSION_INT, zstd.library_version_number())

if __name__ == "__main__":
    unittest.main()
