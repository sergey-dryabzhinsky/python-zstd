# Tests

from tests.base import BaseTestZSTD,tDATA,log,zstd,platform,raise_skip
from.get_memory_usage import get_real_memory_usage
from time import time
import os

class TestZstdSpeed(BaseTestZSTD):

    def test_00_system_info(self):
        log.info("Bundled libzstd uses assembler? : %r" % zstd.ZSTD_with_asm())
        log.info("Bundled libzstd uses threads? :%r" % zstd.ZSTD_with_threads())

    def test_compression_speed3(self):
        wait = 10
        if "ZSTD_FULLTIME_TESTS" in os.environ:
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
        log.info("Compression speed 3 average = %6.2f Mb/sec" % (1.0*sum/1024/1024/wait,))
        log.info("diff Compression memory usage = %6.2f kb" % (1.0*(endMemoryUsage-beginMemoryUsage)/1024,))

    def test_compression_speed19(self):
        wait = 10
        if "ZSTD_FULLTIME_TESTS" in os.environ:
            wait = 30
        log.info("\nWait %d seconds..." % wait)
        sum = 0
        l=len(tDATA)
        tbegin = time()
        beginMemoryUsage=get_real_memory_usage()
        log.info("begin Compression memory usage = %6.2f kb" % (1.0*beginMemoryUsage/1024,))
        while time()-tbegin<wait:
            cdata = zstd.compress(tDATA,19,0)
            sum+=l

        endMemoryUsage=get_real_memory_usage()
        log.info("end Compression memory usage = %6.2f kb" % (1.0*endMemoryUsage/1024,))
        log.info("Compression speed 19 average = %6.2f Mb/sec" % (1.0*sum/1024/1024/wait,))
        log.info("diff Compression memory usage = %6.2f kb" % (1.0*(endMemoryUsage-beginMemoryUsage)/1024,))

    def test_compression_speed_minus1(self):
        wait = 10
        if "ZSTD_FULLTIME_TESTS" in os.environ:
            wait = 30
        log.info("\nWait %d seconds..." % wait)
        sum = 0
        l=len(tDATA)
        tbegin = time()
        beginMemoryUsage=get_real_memory_usage()
        log.info("begin Compression memory usage = %6.2f kb" % (1.0*beginMemoryUsage/1024,))
        while time()-tbegin<wait:
            cdata = zstd.compress(tDATA,-1,0)
            sum+=l

        endMemoryUsage=get_real_memory_usage()
        log.info("end Compression memory usage = %6.2f kb" % (1.0*endMemoryUsage/1024,))
        log.info("Compression speed -1 average = %6.2f Mb/sec" % (1.0*sum/1024/1024/wait,))
        log.info("diff Compression memory usage = %6.2f kb" % (1.0*(endMemoryUsage-beginMemoryUsage)/1024,))

    def test_compression2_speed3_init_context_once(self):
        wait = 10
        if "ZSTD_FULLTIME_TESTS" in os.environ:
            wait = 30
        log.info("\nWait %d seconds..." % wait)
        sum = 0
        l=len(tDATA)
        tbegin = time()
        beginMemoryUsage=get_real_memory_usage()
        log.info("begin Compression2 memory usage = %6.2f kb" % (1.0*beginMemoryUsage/1024,))
        while time()-tbegin<wait:
            cdata = zstd.compress2(tDATA,3,0)
            sum+=l

        endMemoryUsage=get_real_memory_usage()
        log.info("end Compression2 memory usage = %6.2f kb" % (1.0*endMemoryUsage/1024,))
        log.info("Compression2 speed 3 average = %6.2f Mb/sec" % (1.0*sum/1024/1024/wait,))
        log.info("diff Compression2 memory usage = %6.2f kb" % (1.0*(endMemoryUsage-beginMemoryUsage)/1024,))

    def test_compression2_speed19_init_context_once(self):
        wait = 10
        if "ZSTD_FULLTIME_TESTS" in os.environ:
            wait = 30
        log.info("\nWait %d seconds..." % wait)
        sum = 0
        l=len(tDATA)
        tbegin = time()
        beginMemoryUsage=get_real_memory_usage()
        log.info("begin Compression2 memory usage = %6.2f kb" % (1.0*beginMemoryUsage/1024,))
        while time()-tbegin<wait:
            cdata = zstd.compress2(tDATA,19,0)
            sum+=l

        endMemoryUsage=get_real_memory_usage()
        log.info("end Compression2 memory usage = %6.2f kb" % (1.0*endMemoryUsage/1024,))
        log.info("Compression2 speed 19 average = %6.2f Mb/sec" % (1.0*sum/1024/1024/wait,))
        log.info("diff Compression2 memory usage = %6.2f kb" % (1.0*(endMemoryUsage-beginMemoryUsage)/1024,))

    def test_compression2_speed_minus1_init_context_once(self):
        wait = 10
        if "ZSTD_FULLTIME_TESTS" in os.environ:
            wait = 30
        log.info("\nWait %d seconds..." % wait)
        sum = 0
        l=len(tDATA)
        tbegin = time()
        beginMemoryUsage=get_real_memory_usage()
        log.info("begin Compression2 memory usage = %6.2f kb" % (1.0*beginMemoryUsage/1024,))
        while time()-tbegin<wait:
            cdata = zstd.compress2(tDATA,-1,0)
            sum+=l

        endMemoryUsage=get_real_memory_usage()
        log.info("end Compression2 memory usage = %6.2f kb" % (1.0*endMemoryUsage/1024,))
        log.info("Compression2 speed -1 average = %6.2f Mb/sec" % (1.0*sum/1024/1024/wait,))
        log.info("diff Compression2 memory usage = %6.2f kb" % (1.0*(endMemoryUsage-beginMemoryUsage)/1024,))

    def test_compression_speed_no_cpu_cores_cache(self):
        wait = 10
        if "ZSTD_FULLTIME_TESTS" in os.environ:
            wait = 30
        log.info("\nWait %d seconds..." % wait)
        sum = 0
        l=len(tDATA)
        tbegin = time()
        beginMemoryUsage=get_real_memory_usage()
        log.info("begin Compression memory usage = %6.2f kb" % (1.0*beginMemoryUsage/1024,))
        zstd.ZSTD_stopCpuCoresCache()
        while time()-tbegin<wait:
            cdata = zstd.compress(tDATA,3,0)
            sum+=l

        endMemoryUsage=get_real_memory_usage()
        log.info("end Compression memory usage = %6.2f kb" % (1.0*endMemoryUsage/1024,))
        log.info("Compression speed average = %6.2f Mb/sec" % (1.0*sum/1024/1024/wait,))
        log.info("diff Compression memory usage = %6.2f kb" % (1.0*(endMemoryUsage-beginMemoryUsage)/1024,))

    def test_compression_one_thread_speed(self):
        wait = 10
        if "ZSTD_FULLTIME_TESTS" in os.environ:
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
        wait = 10
        if "ZSTD_FULLTIME_TESTS" in os.environ:
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
        wait = 10
        if "ZSTD_FULLTIME_TESTS" in os.environ:
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
        wait = 10
        if "ZSTD_FULLTIME_TESTS" in os.environ:
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

    def test_cpu_cores_cache_default_speed(self):
        wait = 10
        if "ZSTD_FULLTIME_TESTS" in os.environ:
            wait = 70
        log.info("\nWait %d seconds..." % wait)
        ops = 0
        tbegin = time()
        beginMemoryUsage=get_real_memory_usage()
        log.info("begin Check memory usage= %6.2f kb" % (1.0*beginMemoryUsage/1024,))
        while time()-tbegin<wait:
            cores = zstd.ZSTD_threads_count()
            ops+=1

        endMemoryUsage=get_real_memory_usage()
        log.info("end Check memory usage = %6.2f kb" % (1.0*endMemoryUsage/1024,))
        log.info("Check cache use speed(default) average = %6.2f Ops/sec" % (1.0*ops/wait,))
        log.info("diff Check memory usage = %6.2f kb" % (1.0*(endMemoryUsage-beginMemoryUsage)/1024,))

    def test_cpu_cores_cache_none_speed(self):
        wait = 10
        if "ZSTD_FULLTIME_TESTS" in os.environ:
            wait = 70
        log.info("\nWait %d seconds..." % wait)
        ops = 0
        tbegin = time()
        beginMemoryUsage=get_real_memory_usage()
        zstd.ZSTD_stopCpuCoresCache()
        log.info("begin Check memory usage= %6.2f kb" % (1.0*beginMemoryUsage/1024,))
        while time()-tbegin<wait:
            cores = zstd.ZSTD_threads_count()
            ops+=1

        endMemoryUsage=get_real_memory_usage()
        log.info("end Check memory usage = %6.2f kb" % (1.0*endMemoryUsage/1024,))
        log.info("Check cache use speed(0) average = %6.2f Ops/sec" % (1.0*ops/wait,))
        log.info("diff Check memory usage = %6.2f kb" % (1.0*(endMemoryUsage-beginMemoryUsage)/1024,))
    
    def test_cpu_cores_cache_60_speed(self):
        wait = 10
        if "ZSTD_FULLTIME_TESTS" in os.environ:
            wait = 70
        log.info("\nWait %d seconds..." % wait)
        ops = 0
        tbegin = time()
        beginMemoryUsage=get_real_memory_usage()
        log.info("begin Check memory usage= %6.2f kb" % (1.0*beginMemoryUsage/1024,))
        while time()-tbegin<wait:
            cores = zstd.ZSTD_threads_count()
            ops+=1

        endMemoryUsage=get_real_memory_usage()
        log.info("end Check memory usage = %6.2f kb" % (1.0*endMemoryUsage/1024,))
        log.info("Check cache use speed(60) average = %6.2f Ops/sec" % (1.0*ops/wait,))
        log.info("diff Check memory usage = %6.2f kb" % (1.0*(endMemoryUsage-beginMemoryUsage)/1024,))
        
    def test_cpu_cores_cache_01_speed(self):
        wait = 10
        if "ZSTD_FULLTIME_TESTS" in os.environ:
            wait = 70
        log.info("\nWait %d seconds..." % wait)
        ops = 0
        tbegin = time()
        beginMemoryUsage=get_real_memory_usage()
        zstd.ZSTD_setCpuCoresCacheTTL(1)
        log.info("begin Check memory usage= %6.2f kb" % (1.0*beginMemoryUsage/1024,))
        while time()-tbegin<wait:
            cores = zstd.ZSTD_threads_count()
            ops+=1

        endMemoryUsage=get_real_memory_usage()
        log.info("end Check memory usage = %6.2f kb" % (1.0*endMemoryUsage/1024,))
        log.info("Check cache use speed(1) average = %6.2f Ops/sec" % (1.0*ops/wait,))
        log.info("diff Check memory usage = %6.2f kb" % (1.0*(endMemoryUsage-beginMemoryUsage)/1024,))

    def test_cpu_cores_cache_05_speed(self):
        wait = 10
        if "ZSTD_FULLTIME_TESTS" in os.environ:
            wait = 70
        log.info("\nWait %d seconds..." % wait)
        ops = 0
        tbegin = time()
        beginMemoryUsage=get_real_memory_usage()
        zstd.ZSTD_setCpuCoresCacheTTL(5)
        log.info("begin Check memory usage= %6.2f kb" % (1.0*beginMemoryUsage/1024,))
        while time()-tbegin<wait:
            cores = zstd.ZSTD_threads_count()
            ops+=1

        endMemoryUsage=get_real_memory_usage()
        log.info("end Check memory usage = %6.2f kb" % (1.0*endMemoryUsage/1024,))
        log.info("Check cache use speed(5) average = %6.2f Ops/sec" % (1.0*ops/wait,))
        log.info("diff Check memory usage = %6.2f kb" % (1.0*(endMemoryUsage-beginMemoryUsage)/1024,))

    def test_cpu_cores_cache_10_speed(self):
        wait = 10
        if "ZSTD_FULLTIME_TESTS" in os.environ:
            wait = 70
        log.info("\nWait %d seconds..." % wait)
        ops = 0
        tbegin = time()
        beginMemoryUsage=get_real_memory_usage()
        zstd.ZSTD_setCpuCoresCacheTTL(10)
        log.info("begin Check memory usage= %6.2f kb" % (1.0*beginMemoryUsage/1024,))
        while time()-tbegin<wait:
            cores = zstd.ZSTD_threads_count()
            ops+=1

        endMemoryUsage=get_real_memory_usage()
        log.info("end Check memory usage = %6.2f kb" % (1.0*endMemoryUsage/1024,))
        log.info("Check cache use speed(10) average = %6.2f Ops/sec" % (1.0*ops/wait,))
        log.info("diff Check memory usage = %6.2f kb" % (1.0*(endMemoryUsage-beginMemoryUsage)/1024,))
    
if __name__ == '__main__':
    unittest.main()
  
