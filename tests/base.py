# -*- coding: utf-8 -*-

import os
import sys
import logging

import unittest

# Dirty hack, on 2.6 tests are ok always
# UnitTest2 not clearly works with setuptools
if sys.version_info < (2, 7):
    def raise_skip(msg):
        return None
else:
    def raise_skip(msg):
        raise unittest.SkipTest(msg)

import zstd

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('ZSTD')
log.info("Python version: %s" % sys.version)

# Classic lorem ipsum
# + За словесными горами
bDATA = 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.'+\
    ' Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.'+\
    ' Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan'+\
    ' et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi.'
uDATA =\
    ' И немного юникода.'+\
    ' Далеко-далеко за словесными горами в стране гласных и согласных живут рыбные тексты.'+\
    ' Вдали от всех живут они в буквенных домах на берегу Семантика большого языкового океана.'+\
    ' Маленький ручеек Даль журчит по всей стране и обеспечивает ее всеми необходимыми правилами.'+\
    ' Эта парадигматическая страна, в которой жаренные члены предложения залетают прямо в рот.'+\
    ' Даже всемогущая пунктуация не имеет власти над рыбными текстами, ведущими безорфографичный образ жизни.'
tDATA = bDATA + uDATA
if sys.hexversion >= 0x03000000:
    tDATA = tDATA.encode()

class BaseTestZSTD(unittest.TestCase):

    VERSION = "1.5.1"
    VERSION_INT = 10501
    VERSION_INT_MIN = 1 * 100*100 + 0 * 1*100 + 0
    PKG_VERSION = "1.5.1.0"

    def helper_version(self):
        self.assertEqual(self.PKG_VERSION, zstd.version())

    def helper_zstd_version(self):
        if zstd.ZSTD_external():
            return raise_skip("PyZstd was build with external version of ZSTD library (%s). It can be any version. Almost." % zstd.ZSTD_version())
        self.assertEqual(self.VERSION, zstd.ZSTD_version())

    def helper_zstd_version_number_min(self):
        self.assertFalse(self.VERSION_INT_MIN > zstd.ZSTD_version_number(), msg="PyZstd %s require external library version >= 1.0.0!" % zstd.version())

    def helper_zstd_version_number(self):
        if zstd.ZSTD_external():
            return raise_skip("PyZstd was build with external version of ZSTD library (%s). It can be any version. Almost." % zstd.ZSTD_version())
        self.assertEqual(self.VERSION_INT, zstd.ZSTD_version_number())

    def helper_compression_random(self):
        DATA = os.urandom(128 * 1024)  # Read 128kb
        self.assertEqual(DATA, zstd.loads(zstd.dumps(DATA)))

    def helper_compression_default_level(self):
        CDATA = zstd.compress(tDATA)
        self.assertEqual(tDATA, zstd.decompress(CDATA))

    def helper_compression_default_level_zero(self):
        CDATA = zstd.compress(tDATA)
        self.assertEqual(CDATA, zstd.compress(tDATA, 0))

    def helper_compression_default_level_default(self):
        CDATA = zstd.compress(tDATA)
        self.assertEqual(CDATA, zstd.compress(tDATA, 3))

    def helper_compression_negative_level(self):
        if zstd.ZSTD_version_number() < 10304:
            return raise_skip("PyZstd was build with old version of ZSTD library (%s) without support of negative compression levels." % zstd.ZSTD_version())

        CDATA = zstd.compress(tDATA, -1)
        self.assertEqual(tDATA, zstd.decompress(CDATA))

    def helper_compression_negative_level_notdefault(self):
        if zstd.ZSTD_version_number() < 10304:
            return raise_skip("PyZstd was build with old version of ZSTD library (%s) without support of negative compression levels." % zstd.ZSTD_version())

        CDATA = zstd.compress(tDATA, -1)
        self.assertNotEqual(CDATA, zstd.compress(tDATA, 0))

    def helper_compression_wrong_level(self):
        self.assertRaises(zstd.Error, zstd.compress, tDATA, 100)

    def helper_compression_multi_thread_one(self):
        CDATA = zstd.compress(tDATA, 6, 1)
        self.assertEqual(tDATA, zstd.decompress(CDATA))

    def helper_compression_multi_thread_many(self):
        CDATA = zstd.compress(tDATA, 6, 16)
        self.assertEqual(tDATA, zstd.decompress(CDATA))

    def helper_compression_level1(self):
        if sys.hexversion < 0x03000000:
            DATA = 'This is must be very very long string to be compressed by zstd. AAAAAAAAAAAAARGGHHH!!! Just hope its enough length. И немного юникода.'
        else:
            DATA = b'This is must be very very long string to be compressed by zstd. AAAAAAAAAAAAARGGHHH!!! Just hope its enough length.' + 'И немного юникода.'.encode()
        self.assertEqual(DATA, zstd.decompress(zstd.compress(DATA, 1)))

    def helper_compression_level6(self):
        if sys.hexversion < 0x03000000:
            DATA = "This is must be very very long string to be compressed by zstd. AAAAAAAAAAAAARGGHHH!!! Just hope its enough length. И немного юникода."
        else:
            DATA = b"This is must be very very long string to be compressed by zstd. AAAAAAAAAAAAARGGHHH!!! Just hope its enough length." + " И немного юникода.".encode()
        self.assertEqual(DATA, zstd.decompress(zstd.compress(DATA, 6)))

    def helper_compression_level20(self):
        if sys.hexversion < 0x03000000:
            DATA = "This is must be very very long string to be compressed by zstd. AAAAAAAAAAAAARGGHHH!!! Just hope its enough length. И немного юникода."
        else:
            DATA = b"This is must be very very long string to be compressed by zstd. AAAAAAAAAAAAARGGHHH!!! Just hope its enough length." + " И немного юникода.".encode()
        self.assertEqual(DATA, zstd.decompress(zstd.compress(DATA, 20)))
