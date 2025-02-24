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
import platform

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('ZSTD')
log.info("Python version: %s" % sys.version)
log.info("Machine:%s; processor:%s; system:%r; release:%r" % ( platform.machine(), platform.processor(), platform.system(), platform.release()))
log.info("libzstd linked external:%r"% zstd.ZSTD_external())
log.info("libzstd built with legacy formats support:%r"% zstd.ZSTD_legacy_support())
log.info("zstd max number of threads:%r"% zstd.ZSTD_max_threads_count())
log.info("zstd found CPU cores :%r"% zstd.ZSTD_threads_count())
log.info("zstd max compression level:%r"% zstd.ZSTD_max_compression_level())
log.info("zstd min compression level:%r"% zstd.ZSTD_min_compression_level())
log.info("pyzstd module version: %r"% zstd.version())
log.info("libzstd version: %r"% zstd.ZSTD_version())


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

    VERSION = "1.5.6"
    VERSION_INT = 10506
    VERSION_INT_MIN = 1 * 100*100 + 0 * 1*100 + 0
    PKG_VERSION = "1.5.6.6"

    def helper_version(self):
        if zstd.ZSTD_external():
            return raise_skip("PyZstd was build with external version of ZSTD library, so module is like (%s). It can be any version. Almost." % zstd.version())
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

    #def helper_compression_wrong_level(self):
    #    self.assertRaises(zstd.Error, zstd.compress, tDATA, 100)

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

    def helper_compression_empty_string(self):
        # https://github.com/sergey-dryabzhinsky/python-zstd/issues/80
        # An empty string should be able to be compressed and decompressed
        # All levels 1-20 are tested, just to be safe.
        data = b""

        for level in range(0, 20):
            self.assertEqual(data, zstd.decompress(zstd.compress(data, level + 1)))

    def helper_compression_multiple_blocks(self):
        # https://github.com/sergey-dryabzhinsky/python-zstd/issues/94
        # An conctenaed blocks should be able to be decompressed
        if sys.hexversion < 0x03000000:
            import codecs
            data = codecs.decode("28b52ffd200631000068656c6c6f0a28b52ffd2006310000776f726c640a", 'hex_codec')
            odata = "hello\nworld\n"
        else:
            data = bytes.fromhex("28b52ffd200631000068656c6c6f0a28b52ffd2006310000776f726c640a")
            odata = b"hello\nworld\n"

        self.assertEqual(odata, zstd.decompress(data))
