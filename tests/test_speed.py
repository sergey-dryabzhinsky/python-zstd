# Tests

from tests.base import BaseTestZSTD,tDATA,log,zstd
from time import time

class TestZstdSpeed(BaseTestZSTD):

    def test_system_info(self):
        log.info("Bundled libzstd uses assembler? : %r" % zstd.ZSTD_with_asm())
        log.info("Bundled libzstd uses threads? :%r" % zstd.ZSTD_with_threads())

    def test_compressio_speed(self):
        log.info("Compression speed average. Wait 60 seconds...")
        sec = 60
        sum = 0
        l=len(tDATA)
        tbegin = time()
        while time()-tbegin<sec:
            cdata = zstd.compress(tDATA)
            sum+=l

        log.info("Compression speed average =%r b/sec" % (1.0*sum/sec,))

if __name__ == '__main__':
    unittest.main()
  
