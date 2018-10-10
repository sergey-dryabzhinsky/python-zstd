# -*- encoding: utf-8 -*-
# Tests

import os
import sys
import zstd
from tests.base import BaseTestZSTD

# Compatibility notes:
# Explicit Unicode literals (u"") are available starting in Python 2.0.
# Explicit byte literals (b"") are available starting in Python 2.6.
# Python 3.x does not let you put unescaped non-ASCII characters in
# byte literals.
#
# To use string literal concatenation with prefixed literals, you have
# to put the same prefix on every literal in the group (unlike in C,
# where a single prefix suffices).

# Classic lorem ipsum + За словесными горами
tDATA1 = (
    u"Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam "
    u"nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat "
    u"volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation "
    u"ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. "
    u"Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse "
    u"molestie consequat, vel illum dolore eu feugiat nulla facilisis at "
    u"vero eros et accumsan et iusto odio dignissim qui blandit praesent "
    u"luptatum zzril delenit augue duis dolore te feugait nulla facilisi. "
    u"И немного юникода. Далеко-далеко за словесными горами в стране "
    u"гласных и согласных живут рыбные тексты. Вдали от всех живут они "
    u"в буквенных домах на берегу Семантика большого языкового океана. "
    u"Маленький ручеек Даль журчит по всей стране и обеспечивает ее всеми "
    u"необходимыми правилами. Эта парадигматическая страна, в которой "
    u"жаренные члены предложения залетают прямо в рот. Даже всемогущая "
    u"пунктуация не имеет власти над рыбными текстами, ведущими "
    u"безорфографичный образ жизни."
).encode("utf-8")

tDATA2 = (
    u"This is must be very very long string to be compressed by zstd. "
    u"AAAAAAAAAAARGGHHH!!! Just hope its enough length. И немного юникода."
).encode("utf-8")

# legacy compression format produced by pyzstd 0.3.6
tDATA_036 = (
    u"This is must be very very long string to be compressed by zstd "
    u"version 0.3.6. AAAAAAAAAAARGGHHH!!! Just hope its enough length. "
    u"И немного юникода."
).encode("utf-8")
CDATA_036 = (
    b"\xa1\x00\x00\x00#\xb5/\xfd\x00\x00\x97\\\x02\x00\x11\x00$\x80\xc1\t\xe0"
    b"k)?\x8d\x0b\x82g\xb4\x18\x93oK/\x95\xccD\x88\x94\xce7\x9a\x956\xa32\x01"
    b"[\xaf\xf5u7\x03\x16\x00\x18\x00\x18\x00f\xcf\xc5U\xb3\x07\x1dO1%O1%\'"
    b"\xe3\xd5\xe8\xb1:\xabk\x87\x83%X\x01?\xe84\xa6\xe4f5\xe1\x89q\x93\xaa"
    b"\x19\xa1\x07\"\x9c\x8c\xe1\x06\xec\xa5\xe3\xc6\"\xf8\xd2\xba\xce\t\xc1"
    b"\xe6\xd5\xa8\xe0$I\x96eQ\x14\x03\xc1+\x8bq\xc7\xabG\x0e9uE\x80\xab7^"
    b"\x9d:\xc0\x1f\xa7\xee\xc5\xbd\xda\x06\x01\x00T\x01\x10\x00\x00\x18"
    b"\xc2\x1f\xc0\x00\x00"
)

# legacy compression format produced by pyzstd 0.4.6
tDATA_046 = (
    u"This is must be very very long string to be compressed by zstd "
    u"version 0.4.6. AAAAAAAAAAARGGHHH!!! Just hope its enough length. "
    u"И немного юникода."
).encode("utf-8")
CDATA_046 = (
    b"\xa1\x00\x00\x00$\xb5/\xfd\x00\x00\x00\x97\x14\x02\xc0\x0f\x00#\x909"
    b"\x01@\x06+X8\xaaG\xc1k\\\x1eVfA\xfb3\x13R\xaa\xdf?\x85\xd30\xb8T\xc4"
    b"\x1d\xd4\xcc+\x04\x15\x00\x17\x00\x15\x00\x1a\xdd\xe0\x8b\xe2\xbaAu"
    b"\xa6(\x11N\xc6q\xa5\xc7\xfb\xbc\xcf\x19\x02\x8aR\x18\x98\tX\x80\x01"
    b"\x0c\xf5m\x137\xe1\x89q\x93\xbb\x19A\x8f\x1e\x02\x8b\x9b\xb9\xd8`:"
    b"vMR\x98\xde\xf8\x9c\x90:\x82\xd7Z\xcb\xb2\x04\x8cq\xc7\xabG\x0e9u"
    b"\xc5\xc4\xd5\x1b\xafN]\xf2\xc7\xa9;\x05\x00T\x00\x80\r\x00\x80\xb3"
    b"\x18Th\x00l$@\xc5\x11\x0c*\xc0\x00\x00"
)

class TestZSTD(BaseTestZSTD):

    def test_compression_random(self):
        DATA = os.urandom(128 * 1024)  # Read 128kb
        self.assertEqual(DATA, zstd.decompress(zstd.compress(DATA)))

    def test_compression_default_level(self):
        CDATA = zstd.compress(tDATA1)
        self.assertEqual(tDATA1, zstd.decompress(CDATA))

    def test_compression_default_level_zero(self):
        CDATA = zstd.compress(tDATA1)
        self.assertEqual(CDATA, zstd.compress(tDATA1, 0))

    def test_compression_default_level_default(self):
        CDATA = zstd.compress(tDATA1)
        self.assertEqual(CDATA, zstd.compress(tDATA1, 3))

    def test_compression_negative_level(self):
        if zstd.library_version_number() < 10304:
            self.skipTest("PyZstd was build with old version of ZSTD "
                          "library (%s) without support of negative "
                          "compression levels." % zstd.library_version())

        CDATA = zstd.compress(tDATA1, -1)
        self.assertEqual(tDATA1, zstd.decompress(CDATA))

    def test_compression_negative_level_notdefault(self):
        if zstd.library_version_number() < 10304:
            self.skipTest("PyZstd was build with old version of ZSTD "
                          "library (%s) without support of negative "
                          "compression levels." % zstd.library_version())

        CDATA = zstd.compress(tDATA1, -1)
        self.assertNotEqual(CDATA, zstd.compress(tDATA1, 0))

    def test_compression_wrong_level(self):
        self.assertRaises(zstd.Error, zstd.compress, tDATA1, 100)

    def test_compression_level1(self):
        self.assertEqual(tDATA2, zstd.decompress(zstd.compress(tDATA2, 1)))

    def test_compression_level6(self):
        self.assertEqual(tDATA2, zstd.decompress(zstd.compress(tDATA2, 6)))

    def test_compression_level20(self):
        self.assertEqual(tDATA2, zstd.decompress(zstd.compress(tDATA2, 20)))

    def test_compression_old_default_level(self):
        if not self.PYZSTD_LEGACY:
            self.skipTest("PyZstd was build without legacy functions support")

        self.assertEqual(tDATA2, zstd.decompress_old(zstd.compress_old(tDATA2)))

    def test_decompression_v036(self):
        if not self.LEGACY or not self.PYZSTD_LEGACY:
            self.skipTest("PyZstd was build without legacy zstd format "
                          "and functions support")
        self.assertEqual(tDATA_036, zstd.decompress_old(CDATA_036))

    def test_decompression_v046(self):
        if not self.LEGACY or not self.PYZSTD_LEGACY:
            self.skipTest("PyZstd was build without legacy zstd format "
                          "and functions support")
        self.assertEqual(tDATA_046, zstd.decompress_old(CDATA_046))
