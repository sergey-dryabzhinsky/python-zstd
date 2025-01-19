# Tests

import sys
from tests.base import BaseTestZSTD, zstd, tDATA, log

class TestZstdDecompress(BaseTestZSTD):

    def test_decompression_null(self):
        if sys.hexversion < 0x03000000:
            DATA = ''
        else:
            DATA =b''
        self.assertRaises(zstd.Error, zstd.uncompress, zstd.compress(DATA)+b' ')

    def test_check(self):
        cdata = zstd.compress(tDATA)
        log.info("zstd compressed data check:%r" % zstd.check(cdata))
        self.assertEqual(1, zstd.check, cdata)

