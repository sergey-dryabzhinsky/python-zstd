# Tests

import os
from .base import BaseTestZSTD

class TestZSTD(BaseTestZSTD):

    def setUp(self):
        if os.getenv("LEGACY"):
            self.LEGACY = True

    def test_compression_random(self):
        BaseTestZSTD.helper_compression_random(self)

    def test_compression_default_level(self):
        BaseTestZSTD.helper_compression_default_level(self)

    def test_compression_level1(self):
        BaseTestZSTD.helper_compression_level1(self)

    def test_compression_level6(self):
        BaseTestZSTD.helper_compression_level6(self)

    def test_compression_level20(self):
        BaseTestZSTD.helper_compression_level20(self)

    def test_decompression_v036(self):
        if self.LEGACY:
            BaseTestZSTD.helper_decompression_v036(self)

    def test_decompression_v046(self):
        if self.LEGACY:
            BaseTestZSTD.helper_decompression_v046(self)

if __name__ == '__main__':
    unittest.main()
