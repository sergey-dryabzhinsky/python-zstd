# Tests

from tests.base import BaseTestZSTD,tDATA,log,zstd
import time

class TestZstdSpeed(BaseTestZSTD):

    def test_system_info(self):
        log.info("Bundled libzstd uses assembler? :")
        log.info("Bundled libzstd uses threads? :")
        (self)

    def test_compressio_speed(self):
        log.info("Compression speed average = b/sec")
        sec = 60
        sum = 0
        l=len(tDATA)
        tbegin = time.time()
        while time.time()-tbegin!=sec:
            cdata = zstd.compress(tDATA)
            sum+=l

         log.info("Compression speed average =%.%f b/sec" % (1.0*sum/sec))

if __name__ == '__main__':
    unittest.main()
  
