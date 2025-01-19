# Tests

from tests.base import BaseTestZSTD, zstd

class TestZstdDecompress(BaseTestZSTD):

    def test_decompression_error(self):
        if sys.hexversion < 0x03000000:
            DATA = ''
        else:
            DATA = b''
        zstd.uncompress(DATA)

  
