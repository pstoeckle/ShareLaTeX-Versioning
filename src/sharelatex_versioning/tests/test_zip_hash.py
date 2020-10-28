"""
Test.
"""

import unittest
from os.path import join

from pkg_resources import resource_filename

from sharelatex_versioning.download_zip import hash_file, hash_files_in_zip


class MyTestCase(unittest.TestCase):
    def test_something(self):
        current_dir = resource_filename("sharelatex_versioning.tests.rsc", "")
        path_t1 = join(current_dir, "t.zip")
        path_t2 = join(current_dir, "t2.zip")
        path_t3 = join(current_dir, "t3.zip")
        self.assertNotEqual(hash_file(path_t1), hash_file(path_t2))
        self.assertEqual(hash_files_in_zip(path_t1), hash_files_in_zip(path_t2))
        self.assertNotEqual(hash_files_in_zip(path_t1), hash_files_in_zip(path_t3))


if __name__ == "__main__":
    unittest.main()
