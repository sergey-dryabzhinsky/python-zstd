# Regression test for https://github.com/sergey-dryabzhinsky/python-zstd/pull/321
#
# Before the fix, py_zstd_compress_mt2 shared a single global ZSTD_CCtx
# across all calls. Because ZSTD_compress2 releases the GIL, two threads
# calling zstd.compress2 could use the context concurrently and corrupt
# it, leading to out-of-bounds reads inside zstd.
#
# A second race existed as well: with different `level` values the
# global context was freed and recreated while another thread was still
# compressing into it.
#
# This test runs many threads that all call zstd.compress2 with a mix
# of levels, and it must complete without raising and with every output
# round-tripping through zstd.decompress.

import threading
import unittest

import zstd


class TestZstdThreadSafety(unittest.TestCase):
    # Small enough for CI, large enough that the threads actually overlap
    # inside ZSTD_compress2.
    DATA = b"hello world this is a test " * 40000  # ~1.1 MB
    THREADS = 32
    ITERS = 100
    # Mix of levels used to trigger the reset_cContext race in older
    # revisions. Kept here to exercise the pool with contexts that would
    # have been reconfigured before.
    LEVELS = [1, 3, 5, 9, 3, 1]

    def test_compress2_is_thread_safe(self):
        errors = []
        errors_lock = threading.Lock()

        def worker():
            try:
                for i in range(self.ITERS):
                    level = self.LEVELS[i % len(self.LEVELS)]
                    compressed = zstd.compress2(self.DATA, level)
                    self.assertEqual(self.DATA, zstd.decompress(compressed))
            except BaseException as exc:
                with errors_lock:
                    errors.append(exc)

        threads = [
            threading.Thread(target=worker) for _ in range(self.THREADS)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(
            [], errors,
            msg="zstd.compress2 raised under concurrent use: %r" % errors,
        )


if __name__ == '__main__':
    unittest.main()
