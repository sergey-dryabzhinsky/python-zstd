# Tests

import sys
from tests.base import BaseTestZSTD, zstd

class TestZstdDecompress(BaseTestZSTD):

    def test_decompression_null(self):
        if sys.hexversion < 0x03000000:
            DATA = ''
        else:
            DATA =b''
        self.assertRaises(zstd.Error, zstd.uncompress, zstd.compress(DATA)+b' ')
  
    def test_check(self)
        self.assertEquals(1, zstd.ZSTD_check, zstd.compress(DATA))
  
