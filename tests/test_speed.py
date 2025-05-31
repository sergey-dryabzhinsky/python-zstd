# Tests

from tests.base import BaseTestZSTD,tDATA,log,zstd,platform,raise_skip
from.get_memory_usage import get_real_memory_usage
from time import time
import os

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
        beginMemoryUsage=get_real_memory_usage()
        log.info("begin Compression memory usage = %6.2f kb" % (1.0*beginMemoryUsage/1024,))
        while time()-tbegin<wait:
            cdata = zstd.compress(tDATA,3,0)
            sum+=l

        endMemoryUsage=get_real_memory_usage()
        log.info("end Compression memory usage = %6.2f kb" % (1.0*endMemoryUsage/1024,))
        log.info("Compression speed average = %6.2f Mb/sec" % (1.0*sum/1024/1024/wait,))
        log.info("diff Compression memory usage = %6.2f kb" % (1.0*(endMemoryUsage-beginMemoryUsage)/1024,))

    def test_compression_one_thread_speed(self):
        wait = 30
        log.info("\nWait %d seconds..." % wait)
        sum = 0
        l=len(tDATA)
        tbegin = time()
        beginMemoryUsage=get_real_memory_usage()
        log.info("begin Compression with one thread memory usage = %6.2f kb" % (1.0*beginMemoryUsage/1024,))
        while time()-tbegin<wait:
            cdata = zstd.compress(tDATA*10,3,1)
            sum+=l

        endMemoryUsage=get_real_memory_usage()
        log.info("end Compression with one thread memory usage = %6.2f kb" % (1.0*endMemoryUsage/1024,))
        log.info("Compression speed with one thread average = %6.2f Mb/sec" % (1.0*sum/1024/1024/wait,))
        log.info("diff Compression with one thread memory usage = %6.2f kb" % (1.0*(endMemoryUsage-beginMemoryUsage)/1024,))

    def test_decompression_block_speed(self):
        wait = 30
        log.info("\nWait %d seconds..." % wait)
        sum = 0
        cdata = zstd.compress(tDATA)
        l=len(cdata*10)
        tbegin = time()
        while time()-tbegin<wait:
            data = zstd.decompress(cdata*10)
            sum+=l

        log.info("Decompression of block data speed average = %6.2f Mb/sec" % (1.0*sum/1024/1024/wait,))

    def test_decompression_stream_speed(self):
        wait = 30
        log.info("\nWait %d seconds..." % wait)
        sum = 0
#        cdata = zstd.compress(tDATA)
#        cdata = b'\x28\xb5\x2f\xfd\x00\x58\x11\x00\x00\x7b\x7d'
#        log.info('debug cwd: %s' % os.getcwd())
        curdir = os.path.dirname(os.path.abspath(__file__))
#        log.info('curdir: %s' % curdir)
#        if platform.system()=='Windows':
#            raise_skip("Windows can't find tests data")
        f = open(curdir+"/test_data/facebook.ico.zst","rb")
        cdata = f.read()
        f.close()
        l=len(cdata*10)
        tbegin = time()
        while time()-tbegin<wait:
            data = zstd.decompress(cdata*10)
            sum+=l

        log.info("Decompression of streamed data speed average = %6.2f Mb/sec" % (1.0*sum/1024/1024/wait,))


    def test_check_speed(self):
        wait = 30
        log.info("\nWait %d seconds..." % wait)
        sum = 0
        cdata = zstd.compress(tDATA)
        l=len(cdata*10)
        tbegin = time()
        beginMemoryUsage=get_real_memory_usage()
        log.info("begin Check memory usage = %6.2f kb" % (1.0*beginMemoryUsage/1024,))
        while time()-tbegin<wait:
            data = zstd.check(cdata*10)
            sum+=l

        endMemoryUsage=get_real_memory_usage()
        log.info("end Check memory usage = %6.2f kb" % (1.0*endMemoryUsage/1024,))
        log.info("Check speed average = %6.2f Mb/sec" % (1.0*sum/1024/1024/wait,))
        log.info("diff Check memory usage = %6.2f kb" % (1.0*(endMemoryUsage-beginMemoryUsage)/1024,))
    
if __name__ == '__main__':
    unittest.main()
  
