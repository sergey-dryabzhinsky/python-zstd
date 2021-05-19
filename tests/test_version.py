# Tests

from tests.base import BaseTestZSTD

class TestZstdVersion(BaseTestZSTD):

    def test_module_version(self):
        BaseTestZSTD.helper_version(self)

    def test_library_version_number_min(self):
        BaseTestZSTD.helper_zstd_version_number_min(self)

    def test_library_version(self):
        BaseTestZSTD.helper_zstd_version(self)

    def test_library_version_number(self):
        BaseTestZSTD.helper_zstd_version_number(self)

if __name__ == '__main__':
    unittest.main()
