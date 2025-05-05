# Tests

from tests.base import BaseTestZSTD,tDATA,log,zstd
from time import time

class TestZstdSpeed(BaseTestZSTD):

    def test_00_system_info(self):
        log.info("Bundled libzstd uses assembler? : %r" % zstd.ZSTD_with_asm())
        log.info("Bundled libzstd uses threads? :%r" % zstd.ZSTD_with_threads())

    def test_compression_speed(self):
        wait = 30
        log.info("\nWait %d seconds..." % wait)
        sum = 0
        l=len(tDATA)
        tbegin = time()
        while time()-tbegin<wait:
            cdata = zstd.compress(tDATA)
            sum+=l

        log.info("Compression speed average = %6f Mb/sec" % (1.0*sum/1024/1024/wait,))

    def test_decompression_block_speed(self):
        wait = 30
        log.info("\nWait %d seconds..." % wait)
        sum = 0
        cdata = zstd.compress(tDATA)
        l=len(cdata)
        tbegin = time()
        while time()-tbegin<wait:
            data = zstd.decompress(cdata)
            sum+=l

        log.info("Decompression of block data speed average = %6f Mb/sec" % (1.0*sum/1024/1024/wait,))

    def test_decompression_stream_speed(self):
        wait = 30
        log.info("\nWait %d seconds..." % wait)
        sum = 0
#        cdata = zstd.compress(tDATA)
#        cdata = b'\x28\xb5\x2f\xfd\x00\x58\x11\x00\x00\x7b\x7d'
        f = open("tests/test_data/facebook.ico.zst","rb")
        cdata = f.read()
        f.close()
        l=len(cdata)
        tbegin = time()
        while time()-tbegin<wait:
            data = zstd.decompress(cdata)
            sum+=l

        log.info("Decompression of streamed datspeed average = %6f Mb/sec" % (1.0*sum/1024/1024/wait,))

    def test_check_speed(self):
        wait = 30
        log.info("\nWait %d seconds..." % wait)
        sum = 0
        cdata = zstd.compress(tDATA)
        l=len(cdata)
        tbegin = time()
        while time()-tbegin<wait:
            data = zstd.check(cdata)
            sum+=l

        log.info("Check speed average = %6f Mb/sec" % (1.0*sum/1024/1024/wait,))
    
if __name__ == '__main__':
    unittest.main()
  
