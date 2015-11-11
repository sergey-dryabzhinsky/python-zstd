import zstd
import sys


import unittest
import os

class TestZSTD(unittest.TestCase):

    def test_random(self):
      DATA = os.urandom(128 * 1024)  # Read 128kb
      self.assertEqual(DATA, zstd.loads(zstd.dumps(DATA)))

    def test_raw(self):
      DATA = b"abc def"
      self.assertEqual(DATA, zstd.decompress(zstd.compress(DATA)))

    def test_level2(self):
      DATA = b"abc def"
      self.assertEqual(DATA, zstd.decompress(zstd.compress(DATA, 2)))

    def test_level6(self):
      DATA = b"abc def"
      self.assertEqual(DATA, zstd.decompress(zstd.compress(DATA, 6)))

    def test_level20(self):
      DATA = b"abc def"
      self.assertEqual(DATA, zstd.decompress(zstd.compress(DATA, 20)))

if __name__ == '__main__':
    unittest.main()


