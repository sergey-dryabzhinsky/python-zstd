# Tests

import sys
from tests.base import BaseTestZSTD, zstd

class TestZstdDecompress(BaseTestZSTD):

    def test_decompression_null(self):
        if sys.hexversion < 0x03000000:
            DATA = ''
        else:
            DATA = b''
        zstd.uncompress(DATA)

  
