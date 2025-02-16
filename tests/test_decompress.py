# Tests

import sys
from tests.base import BaseTestZSTD, zstd, tDATA, log

class TestZstdDecompress(BaseTestZSTD):

    def test_decompression_null(self):
        if sys.hexversion < 0x03000000:
            DATA = ''
        else:
            DATA = b''
        self.assertRaises(zstd.Error, zstd.uncompress, zstd.compress(DATA)+b' ')

    def test_check_compressed(self):
        cdata = zstd.compress(tDATA)
        check = zstd.check(cdata)
        log.info("zstd compressed data check (1):%r" % check)
        self.assertEqual(1, check)

    def test_check_not_compressed(self):
        check = zstd.check(tDATA)
        log.info("zstd not compressed data check (0):%r" % check)
        self.assertEqual(0, check)
        
    def test_check_uncompressed(self):
        cdata = b''
        log.info("zstd uncompressed data check:%r" % zstd.check(cdata))
        self.assertEqual(0, zstd.check(cdata))
        
