# Tests

from tests.base import BaseTestZSTD

class TestZstdCompress(BaseTestZSTD):

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

    def test_compression_wrong_level(self):
        BaseTestZSTD.helper_compression_wrong_level(self)

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
