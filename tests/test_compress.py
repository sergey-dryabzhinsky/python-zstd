# Tests

import os

from tests.base import BaseTestZSTD, raise_skip

class TestZSTD(BaseTestZSTD):

    def setUp(self):
        if os.getenv("LEGACY"):
            self.LEGACY = True
        if os.getenv("PYZSTD_LEGACY"):
            self.PYZSTD_LEGACY = True

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

    def test_compression_old_default_level(self):
        if not self.PYZSTD_LEGACY:
            return raise_skip("PyZstd was build without legacy functions support")
        BaseTestZSTD.helper_compression_old_default_level(self)

    def test_compression_level1(self):
        BaseTestZSTD.helper_compression_level1(self)

    def test_compression_level6(self):
        BaseTestZSTD.helper_compression_level6(self)

    def test_compression_level20(self):
        BaseTestZSTD.helper_compression_level20(self)

    def test_decompression_v036(self):
        if self.LEGACY and self.PYZSTD_LEGACY:
            BaseTestZSTD.helper_decompression_v036(self)
        else:
            return raise_skip("PyZstd was build without legacy zstd format and functions support")

    def test_decompression_v046(self):
        if self.LEGACY and self.PYZSTD_LEGACY:
            BaseTestZSTD.helper_decompression_v046(self)
        else:
            return raise_skip("PyZstd was build without legacy zstd format and functions support")

if __name__ == '__main__':
    unittest.main()
