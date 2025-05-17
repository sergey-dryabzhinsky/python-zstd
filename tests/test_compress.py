# Tests

from tests.base import BaseTestZSTD, zstd, tDATA, log

class TestZstdCompress(BaseTestZSTD):

    def setup(self):
        th = zstd.Thread_pool_init()
        log.info("Stated pool of %d threads" % th)

    def tearDown(self):
        th = zstd.Thread_pool_free()
        log.info("Freed pool of %d threads" % th)

    def test_compression_random(self):
        BaseTestZSTD.helper_compression_random(self)

    def test_compression_default_level(self):
        BaseTestZSTD.helper_compression_default_level(self)

    def test_compression_default_level_zero(self):
        BaseTestZSTD.helper_compression_default_level_zero(self)

    def test_compression_default_level_default(self):
        BaseTestZSTD.helper_compression_default_level_default(self)

    def test_compression_negative_level(self):
        BaseTestZSTD.helper_compression_negative_level(self)

    def test_compression_negative_level_notdefault(self):
        BaseTestZSTD.helper_compression_negative_level_notdefault(self)

    def test_compression_wrong_level_strict(self):
        self.assertRaises(zstd.Error, zstd.compress, tDATA, 100, 0, 1)

    def test_compression_equal_high_level(self):
        cdata1 = zstd.compress(tDATA, 22)
        cdata2 = zstd.compress(tDATA, 2200)
        self.assertEqual(cdata1, cdata2)

    def test_compression_MT_and_not(self):
        cdata1 = zstd.compress(tDATA, 14)
        cdata2 = zstd.compress_real_mt(tDATA, 14)
        self.assertEqual(cdata1, cdata2)

    def test_compression_MT_and_raw(self):
        cdata2 = zstd.compress_real_mt(tDATA, 14)
        data2 = zstd.decompress(cdata2)
        self.assertEqual(tDATA, data2)

    def test_compression_equal_low_level(self):
        cdata1 = zstd.compress(tDATA, -100)
        cdata2 = zstd.compress(tDATA, -1000)
        self.assertEqual(cdata1, cdata2)

    def test_compression_equal_high_threads(self):
        cdata1 = zstd.compress(tDATA, 22, 256)
        cdata2 = zstd.compress(tDATA, 22, 2560)
        self.assertEqual(cdata1, cdata2)
        
    def test_compression_multi_thread_one(self):
        BaseTestZSTD.helper_compression_multi_thread_one(self)

    def test_compression_multi_thread_many(self):
        BaseTestZSTD.helper_compression_multi_thread_many(self)

    def test_compression_level1(self):
        BaseTestZSTD.helper_compression_level1(self)

    def test_compression_level6(self):
        BaseTestZSTD.helper_compression_level6(self)

    def test_compression_level20(self):
        BaseTestZSTD.helper_compression_level20(self)

    def test_compression_empty_string(self):
        BaseTestZSTD.helper_compression_empty_string(self)

    def test_compression_multiple_blocks(self):
        BaseTestZSTD.helper_compression_multiple_blocks(self)


if __name__ == '__main__':
    unittest.main()
