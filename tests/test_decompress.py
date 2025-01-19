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

    def test_check_compressed(self):
        cdata = zstd.compress(tDATA)
        log.info("zstd compressed data check:%r" % zstd.check(cdata))
        self.assertEqual(1, zstd.check(cdata))

    def test_check_uncompressed(self):
        cdata = b'\0'
        log.info("zstd uncompressed data check:%r" % zstd.check(cdata))
        self.assertEqual(0, zstd.check(cdata))
        
