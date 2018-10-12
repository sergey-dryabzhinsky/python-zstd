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
# Tests of constants.
#
class CompressionConstants(BaseTestZSTD):
    def test_constant_types(self):
        self.assertTrue(isinstance(zstd.CLEVEL_MIN, int))
        self.assertTrue(isinstance(zstd.CLEVEL_MAX, int))
        self.assertTrue(isinstance(zstd.CLEVEL_DEFAULT, int))

    def test_constant_relations(self):
        self.assertTrue(zstd.CLEVEL_MIN < zstd.CLEVEL_MAX)
        self.assertTrue(zstd.CLEVEL_MIN < zstd.CLEVEL_DEFAULT)
        self.assertTrue(zstd.CLEVEL_DEFAULT < zstd.CLEVEL_MAX)

        self.assertTrue(zstd.CLEVEL_MIN < 0)
        self.assertTrue(zstd.CLEVEL_MAX > 0)
        self.assertTrue(zstd.CLEVEL_DEFAULT != 0)

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
# Tests of compression format.
#

# current (pyzstd & zstd >= 1.3.4) format
tDATA_134 = (
    u"This is must be very very long string to be compressed by zstd "
    u"version 1.3.4. AAAAAAAAAAARGGHHH!!! Just hope its enough length. "
    u"И немного юникода."
).encode("utf-8")

# These compressed strings were generated with version 1.3.5 of the
# command line utility that ships with libzstd.  This is to ensure
# interoperability with other generators of the Zstandard file format.
# (Of course it's the same library under the hood, so this isn't as
# stringent a test as it could be.)
CDATA_134_DEF = ( # zstd --no-check -3 tDATA_134.txt
    b"\x28\xb5\x2f\xfd\x20\xa1\x3d\x04\x00\x52\x48\x1d\x22\x90\x39\x01"
    b"\x4c\x08\xc1\xc2\x51\x3d\x0a\x5e\xe3\xf2\xb0\x32\x0b\xda\x9f\x99"
    b"\x90\x52\xfd\xfe\x29\x9c\x86\xc1\x4b\x31\xbd\xa0\x66\x5e\x21\x8c"
    b"\x71\xc7\xab\x47\x0e\x39\x75\xc5\xc4\xd5\x1b\xaf\x4e\x5d\xf2\xc7"
    b"\xa9\x7b\x71\x33\x17\x1b\x4c\xc7\xae\x49\x0a\xd3\x1b\x9f\x13\x52"
    b"\x47\xf0\x5a\x6b\x59\x16\x45\x29\x0c\xcc\x04\x2c\xc0\x00\x86\xfa"
    b"\xb6\x89\x9b\xf0\xc4\xb8\xc9\xdd\x8c\xa0\x47\x0f\x1a\xdd\xe0\x8b"
    b"\xe2\xba\x41\x75\xa6\x28\x11\x4e\xc6\x71\xa5\xc7\xfb\xbc\xcf\x19"
    b"\x02\x05\x00\x5e\x08\x1e\x6e\xbf\xa6\x2c\xfc\x69\x15\x0c\x85\x09"
)
CDATA_134_MIN = ( # zstd --no-check --fast=5 tDATA_134.txt
    b"\x28\xb5\x2f\xfd\x20\xa1\x09\x05\x00\x54\x68\x69\x73\x20\x69\x73"
    b"\x20\x6d\x75\x73\x74\x20\x62\x65\x20\x76\x65\x72\x79\x20\x76\x65"
    b"\x72\x79\x20\x6c\x6f\x6e\x67\x20\x73\x74\x72\x69\x6e\x67\x20\x74"
    b"\x6f\x20\x62\x65\x20\x63\x6f\x6d\x70\x72\x65\x73\x73\x65\x64\x20"
    b"\x62\x79\x20\x7a\x73\x74\x64\x20\x76\x65\x72\x73\x69\x6f\x6e\x20"
    b"\x31\x2e\x33\x2e\x34\x2e\x20\x41\x41\x41\x41\x41\x41\x41\x41\x41"
    b"\x41\x41\x52\x47\x47\x48\x48\x48\x21\x21\x21\x20\x4a\x75\x73\x74"
    b"\x20\x68\x6f\x70\x65\x20\x69\x74\x73\x20\x65\x6e\x6f\x75\x67\x68"
    b"\x20\x6c\x65\x6e\x67\x74\x68\x2e\x20\xd0\x98\x20\xd0\xbd\xd0\xb5"
    b"\xd0\xbc\xd0\xbd\xd0\xbe\xd0\xb3\xd0\xbe\x20\xd1\x8e\xd0\xbd\xd0"
    b"\xb8\xd0\xba\xd0\xbe\xd0\xb4\xd0\xb0\x2e"
)
CDATA_134_MAX = ( # zstd --no-check --ultra -22 tDATA_134.txt
    b"\x28\xb5\x2f\xfd\x20\xa1\x35\x04\x00\x92\xc8\x1d\x22\x90\x39\x01"
    b"\x4c\x08\xc1\xc2\x51\x3d\x0a\x5e\xe3\xf2\xb0\xf2\x2f\xda\x99\x84"
    b"\x90\x52\xfd\xfe\x29\x9c\x86\xc1\x4b\x31\xbd\xa0\x66\x5e\x21\x8c"
    b"\x71\xc7\xab\x47\x0e\x39\x75\xc5\xc4\xd5\x1b\xaf\x4e\x5d\xf2\xc7"
    b"\xa9\x7b\x71\x33\xb7\x0d\xa6\x63\xd7\xa4\x08\xd3\xba\xcf\x09\x45"
    b"\xe7\x55\x89\xe0\xb5\xd6\xb2\x2c\x8a\x52\x18\x98\x09\x58\x80\x01"
    b"\x0c\xe3\xd3\x66\x35\xe1\x89\x71\x93\xaa\x19\x41\x4f\x3c\xc4\x75"
    b"\x83\x2f\x5a\x75\x83\xd1\x99\xa2\x44\x38\x19\xaf\x4a\x8f\xf5\x59"
    b"\x9f\x33\x04\x04\x00\xb8\xfd\x9a\xb2\xf0\xa7\x55\x30\x14\x26"
)

# legacy compression format produced by pyzstd 0.3.6
tDATA_036 = (
    u"This is must be very very long string to be compressed by zstd "
    u"version 0.3.6. AAAAAAAAAAARGGHHH!!! Just hope its enough length. "
    u"И немного юникода."
).encode("utf-8")
CDATA_036 = (
    b"\xa1\x00\x00\x00\x23\xb5\x2f\xfd\x00\x00\x97\x5c\x02\x00\x11\x00"
    b"\x24\x80\xc1\x09\xe0\x6b\x29\x3f\x8d\x0b\x82\x67\xb4\x18\x93\x6f"
    b"\x4b\x2f\x95\xcc\x44\x88\x94\xce\x37\x9a\x95\x36\xa3\x32\x01\x5b"
    b"\xaf\xf5\x75\x37\x03\x16\x00\x18\x00\x18\x00\x66\xcf\xc5\x55\xb3"
    b"\x07\x1d\x4f\x31\x25\x4f\x31\x25\x27\xe3\xd5\xe8\xb1\x3a\xab\x6b"
    b"\x87\x83\x25\x58\x01\x3f\xe8\x34\xa6\xe4\x66\x35\xe1\x89\x71\x93"
    b"\xaa\x19\xa1\x07\x22\x9c\x8c\xe1\x06\xec\xa5\xe3\xc6\x22\xf8\xd2"
    b"\xba\xce\x09\xc1\xe6\xd5\xa8\xe0\x24\x49\x96\x65\x51\x14\x03\xc1"
    b"\x2b\x8b\x71\xc7\xab\x47\x0e\x39\x75\x45\x80\xab\x37\x5e\x9d\x3a"
    b"\xc0\x1f\xa7\xee\xc5\xbd\xda\x06\x01\x00\x54\x01\x10\x00\x00\x18"
    b"\xc2\x1f\xc0\x00\x00"
)

# legacy compression format produced by pyzstd 0.4.6
tDATA_046 = (
    u"This is must be very very long string to be compressed by zstd "
    u"version 0.4.6. AAAAAAAAAAARGGHHH!!! Just hope its enough length. "
    u"И немного юникода."
).encode("utf-8")
CDATA_046 = (
    b"\xa1\x00\x00\x00\x24\xb5\x2f\xfd\x00\x00\x00\x97\x14\x02\xc0\x0f"
    b"\x00\x23\x90\x39\x01\x40\x06\x2b\x58\x38\xaa\x47\xc1\x6b\x5c\x1e"
    b"\x56\x66\x41\xfb\x33\x13\x52\xaa\xdf\x3f\x85\xd3\x30\xb8\x54\xc4"
    b"\x1d\xd4\xcc\x2b\x04\x15\x00\x17\x00\x15\x00\x1a\xdd\xe0\x8b\xe2"
    b"\xba\x41\x75\xa6\x28\x11\x4e\xc6\x71\xa5\xc7\xfb\xbc\xcf\x19\x02"
    b"\x8a\x52\x18\x98\x09\x58\x80\x01\x0c\xf5\x6d\x13\x37\xe1\x89\x71"
    b"\x93\xbb\x19\x41\x8f\x1e\x02\x8b\x9b\xb9\xd8\x60\x3a\x76\x4d\x52"
    b"\x98\xde\xf8\x9c\x90\x3a\x82\xd7\x5a\xcb\xb2\x04\x8c\x71\xc7\xab"
    b"\x47\x0e\x39\x75\xc5\xc4\xd5\x1b\xaf\x4e\x5d\xf2\xc7\xa9\x3b\x05"
    b"\x00\x54\x00\x80\x0d\x00\x80\xb3\x18\x54\x68\x00\x6c\x24\x40\xc5"
    b"\x11\x0c\x2a\xc0\x00\x00"
)


class CompressionFormats(BaseTestZSTD):

    def test_compress_std_format(self):
        self.assertEqual(CDATA_134_DEF, zstd.compress(tDATA_134))
        self.assertEqual(CDATA_134_MIN,
                         zstd.compress(tDATA_134, zstd.CLEVEL_MIN))
        self.assertEqual(CDATA_134_MAX,
                         zstd.compress(tDATA_134, zstd.CLEVEL_MAX))

    def test_decompress_std_format(self):
        self.assertEqual(tDATA_134, zstd.decompress(CDATA_134_DEF))
        self.assertEqual(tDATA_134, zstd.decompress(CDATA_134_MIN))
        self.assertEqual(tDATA_134, zstd.decompress(CDATA_134_MAX))

    def test_decompress_rejects_old_format(self):
        self.assertRaises(zstd.Error, zstd.decompress, CDATA_036)
        self.assertRaises(zstd.Error, zstd.decompress, CDATA_046)

    def test_compress_old_roundtrip(self):
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


    def test_decompress_v036(self):
        if not hasattr(zstd, "compress_old"):
            self.skipTest("legacy compression functions not available")
        if not self.LEGACY:
            self.skipTest("legacy format support not available")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertEqual(tDATA_036, zstd.decompress_old(CDATA_036))

    def test_decompress_v046(self):
        if not hasattr(zstd, "compress_old"):
            self.skipTest("legacy compression functions not available")
        if not self.LEGACY:
            self.skipTest("legacy format support not available")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertEqual(tDATA_046, zstd.decompress_old(CDATA_046))
