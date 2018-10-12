# Tests

import os
import zstd

from tests.base import BaseTestZSTD

MIN_LIBRARY_VERSION_NUMBER = 1*100*100 + 3*100 + 4

class VersionNumbers(BaseTestZSTD):

    def test_VERSION(self):
        # zstd.VERSION should have four components,
        # each of them a nonnegative integer
        a, b, c, d = zstd.VERSION.split('.')
        a = int(a)
        b = int(b)
        c = int(c)
        d = int(d)
        self.assertTrue(a >= 0)
        self.assertTrue(b >= 0)
        self.assertTrue(c >= 0)
        self.assertTrue(d >= 0)

    def test_LIBRARY_VERSION(self):
        # zstd.LIBRARY_VERSION should have three components,
        # each of them a nonnegative integer
        a, b, c = zstd.LIBRARY_VERSION.split('.')
        a = int(a)
        b = int(b)
        c = int(c)
        self.assertTrue(a >= 0)
        self.assertTrue(b >= 0)
        self.assertTrue(c >= 0)

    def test_LIBRARY_VERSION_NUMBER(self):
        ver = zstd.LIBRARY_VERSION_NUMBER
        self.assertTrue(ver >= MIN_LIBRARY_VERSION_NUMBER)

        a, b, c = zstd.LIBRARY_VERSION.split('.')
        a = int(a)
        b = int(b)
        c = int(c)
        self.assertEqual(a*100*100 + b*100 + c, ver)

    def test_library_version(self):
        a, b, c = zstd.LIBRARY_VERSION.split('.')
        a = int(a)
        b = int(b)
        c = int(c)

        x, y, z = zstd.library_version().split('.')
        x = int(x)
        y = int(y)
        z = int(z)

        self.assertTrue(x >= a)
        self.assertTrue(x > a or y >= b)
        self.assertTrue(x > a or y > a or z >= c)

    def test_library_version_number(self):
        ver = zstd.library_version_number()
        self.assertTrue(ver >= zstd.LIBRARY_VERSION_NUMBER)
        self.assertTrue(ver >= MIN_LIBRARY_VERSION_NUMBER)

        x, y, z = zstd.library_version().split('.')
        x = int(x)
        y = int(y)
        z = int(z)
        self.assertEqual(x*100*100 + y*100 + z, ver)

if __name__ == "__main__":
    unittest.main()
