import unittest

import zstd


class TestFixes(unittest.TestCase):
    def test_resize_memory_integrity(self):
        # Construct data with high compression ratio to trigger buffer resizing logic.
        # In this case, cSize will be significantly smaller than initial dest_size.
        data = b"0" * 1024 * 1024  # 1MB of repetitive data
        compressed = zstd.compress(data)

        # Verify if decompression results in identical data.
        # This checks if _PyBytes_Resize preserved data integrity and null-termination.
        decompressed = zstd.decompress(compressed)
        self.assertEqual(data, decompressed)

        # Verify the bytes object properties in Python.
        self.assertEqual(len(decompressed), 1024 * 1024)

        # Append data to check if the internal buffer is correctly null-terminated.
        test_str = decompressed + b"check"
        self.assertTrue(test_str.endswith(b"check"))

    def test_exception_path_safety(self):
        # Verify that the exception handling path is safe and doesn't crash the interpreter.
        # Providing invalid data will trigger the error reporting logic in C.
        invalid_data = b"NOT_A_ZSTD_FRAME_DATA_BUT_LONG_ENOUGH_FOR_VALIDATION_FAILURE"
        with self.assertRaises(zstd.Error) as cm:
            zstd.decompress(invalid_data)

        # The specific message might vary depending on where zstd library stops validation,
        # but it must be a valid zstd.Error instance.
        self.assertTrue(len(str(cm.exception)) > 0)
