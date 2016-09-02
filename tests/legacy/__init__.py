# Tests

from ..common.test import BaseTestZSTD

class TestZSTDLegacy(BaseTestZSTD):

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
        BaseTestZSTD.helper_decompression_v036(self)

    def test_decompression_v046(self):
        BaseTestZSTD.helper_decompression_v046(self)

if __name__ == '__main__':
    unittest.main()
