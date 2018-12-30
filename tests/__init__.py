# Tests

import sys

# Another dirty hack for tests
if sys.hexversion < 0x03000000:
    import test_compress
    import test_version
