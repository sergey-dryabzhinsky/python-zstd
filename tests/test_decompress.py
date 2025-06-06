# Tests

import sys, os
from tests.base import BaseTestZSTD, zstd, tDATA, log, raise_skip, platform

class TestZstdDecompress(BaseTestZSTD):

    def test_decompression_null(self):
        if sys.hexversion < 0x03000000:
            DATA = ''
        else:
            DATA = b''
        self.assertRaises(zstd.Error, zstd.uncompress, zstd.compress(DATA)+b' ')

    def test_decompression_streamed(self):
        log.info('debug cwd: %s' % os.getcwd())
        curdir = os.path.dirname(os.path.abspath(__file__))
        log.info('curdir: %s' % curdir)
        if platform.system()=='Windows':
            raise_skip("Windiows can't find tests data")
        f = open(curdir+"/test_data/facebook.ico.zst","rb")
        DATA = f.read()
        f.close()
        log.info('data check, should be 2: %s' % zstd.check(DATA))
        self.assertEqual(2, zstd.check(DATA))
        zstd.uncompress(DATA)
        #self.assertRaises(zstd.Error, zstd.uncompress, DATA)

    def test_decompression_rusted(self):
        #if sys.hexversion < 0x03000000:
        #raise_skip("need python version >= 3")
        if sys.hexversion < 0x03000000:
            data = '{}'
        else:
            data = b'{}'
        cdata = b'\x28\xb5\x2f\xfd\x00\x58\x11\x00\x00\x7b\x7d'
        log.info('data check, should be 2: %s' % zstd.check(cdata))
        self.assertEqual(2, zstd.check(cdata))
        log.info("data must be '{}': %r" % zstd.uncompress(cdata))
        self.assertEqual(data, zstd.uncompress(cdata))
        
    def test_check_compressed(self):
        cdata = zstd.compress(tDATA)
        check = zstd.check(cdata)
        log.info("zstd compressed data check, must be (1):%r" % check)
        self.assertEqual(1, check)

    def test_check_not_compressed(self):
        check = zstd.check(tDATA)
        log.info("zstd not compressed data check, must be (0):%r" % check)
        self.assertEqual(0, check)
        
    def test_check_uncompressed(self):
        cdata = b''
        log.info("zstd uncompressed data check, must be (0):%r" % zstd.check(cdata))
        self.assertEqual(0, zstd.check(cdata))
        
