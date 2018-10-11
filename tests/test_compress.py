# -*- encoding: utf-8 -*-
# Tests

import hashlib
import os
import struct
import sys
import warnings

import zstd
from tests.base import BaseTestZSTD

# Test data.

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

# 128kB of random data, which presumably won't compress very well.
# Take care to read only a few bytes from the OS-level secure RNG.
def gen_random_bytes(length):
    m = hashlib.sha256()
    n, r = divmod(length, m.digest_size)
    out = []
    enc = struct.Struct("<l")
    m.update(os.urandom(16))
    for i in range(n):
        m.update(enc.pack(i))
        out.append(m.digest())

    m.update(enc.pack(0))
    out.append(m.digest()[:r])
    return b"".join(out)

tDATA3 = gen_random_bytes(128 * 1024)

# Synthesize round-trip tests (compress, decompress, result should equal
# original) for the above test strings at all supported compression levels.
def make_compression_roundtrip_tests():
    tdict = {}
    for i, dname in enumerate(["tDATA1", "tDATA2", "tDATA3"]):
        for level in range(zstd.CLEVEL_MIN, zstd.CLEVEL_MAX + 1):
            fname = "test_roundtrip_%02d_%02d" % (i, level)
            fname = fname.replace("-", "m")
            data = globals()[dname]
            def test_one(self, data=data, level=level, dname=dname):
                self.assertEqual(
                    data, zstd.decompress(zstd.compress(data, level)))
            test_one.__name__ = fname
            tdict[fname] = test_one
    return tdict

CompressionRoundTrip = type("CompressionRoundTrip", (BaseTestZSTD,),
                            make_compression_roundtrip_tests())

###
# Compression either without a "level" argument or with zero supplied
# for that argument is supposed to produce the same compressed blob as
# compression with level zstd.CLEVEL_DEFAULT.  We repeat this test with
# all three test strings, as above.

def make_compression_default_tests():
    tdict = {}
    for i, dname in enumerate(["tDATA1", "tDATA2", "tDATA3"]):
        data = globals()[dname]

        fname = "test_no_level_%02d" % i
        def test_no_level(self, data=data):
            cdata1 = zstd.compress(data)
            cdata2 = zstd.compress(data, level=zstd.CLEVEL_DEFAULT)
            self.assertEqual(cdata1, cdata2)
        test_no_level.__name__ = fname
        tdict[fname] = test_no_level

        fname = "test_zero_level_%02d" % i
        def test_zero_level(self, data=data):
            cdata1 = zstd.compress(data, level=0)
            cdata2 = zstd.compress(data, level=zstd.CLEVEL_DEFAULT)
            self.assertEqual(cdata1, cdata2)
        test_zero_level.__name__ = fname
        tdict[fname] = test_zero_level

    return tdict

CompressionDefaults = type("CompressionDefaults", (BaseTestZSTD,),
                           make_compression_default_tests())


###
# Tests of error handling.
#
class CompressionErrors(BaseTestZSTD):
    def test_level_too_high(self):
        self.assertRaises(zstd.Error, zstd.compress, tDATA1,
                          zstd.CLEVEL_MAX + 1)

    def test_level_too_low(self):
        self.assertRaises(zstd.Error, zstd.compress, tDATA1,
                          zstd.CLEVEL_MIN - 1)

    def test_level_not_a_number(self):
        self.assertRaises(TypeError, zstd.compress, tDATA1,
                          "CLEVEL_DEFAULT")

    def test_decompress_nothing(self):
        self.assertRaises(zstd.Error, zstd.decompress, b"")

    def test_decompress_truncated(self):
        CDATA = zstd.compress(tDATA1)
        for i in range(1, len(CDATA)):
            self.assertRaises(zstd.Error, zstd.decompress, CDATA[:i])


###
# Tests of the legacy compression format.
#
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


class TestCompressionLegacy(BaseTestZSTD):

    def test_compression_old_roundtrip(self):
        if not hasattr(zstd, "compress_old"):
            self.skipTest("legacy compression functions not available")

        self.assertTrue(hasattr(zstd, "decompress_old"))

        # As well as the round-trip test, check both functions produce
        # deprecation warnings.
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.assertEqual(
                tDATA2, zstd.decompress_old(zstd.compress_old(tDATA2)))

            self.assertEqual(len(w), 2)
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertTrue("compress_old produces" in str(w[0].message))
            self.assertTrue(issubclass(w[1].category, DeprecationWarning))
            self.assertTrue("decompress_old expects" in str(w[1].message))


    def test_decompression_v036(self):
        if not hasattr(zstd, "compress_old"):
            self.skipTest("legacy compression functions not available")
        if not self.LEGACY:
            self.skipTest("legacy format support not available")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertEqual(tDATA_036, zstd.decompress_old(CDATA_036))

    def test_decompression_v046(self):
        if not hasattr(zstd, "compress_old"):
            self.skipTest("legacy compression functions not available")
        if not self.LEGACY:
            self.skipTest("legacy format support not available")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertEqual(tDATA_046, zstd.decompress_old(CDATA_046))

    def test_new_decompress_rejects_old_format(self):
        self.assertRaises(zstd.Error, zstd.decompress, CDATA_036)
        self.assertRaises(zstd.Error, zstd.decompress, CDATA_046)
