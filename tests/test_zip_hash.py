# Copyright © Patrick Stoeckle 2025 - 2025
#
# Licensed under the Apache License License 2.0
#
# Authors: Patrick Stoeckle
#
# SPDX-FileCopyrightText: 2025 Patrick Stoeckle
#
# SPDX-License-Identifier: Apache-2.0

"""Test."""

from __future__ import annotations

from pathlib import Path
from unittest import TestCase
from unittest import main

from sharelatex_versioning.logic.hash_file import hash_file
from sharelatex_versioning.logic.hash_file import hash_files_in_zip


class MyTestCase(TestCase):
    def test_something(self) -> None:
        """Test something."""
        current_dir = Path("tests/rsc")
        path_t1 = current_dir.joinpath("t.zip")
        path_t2 = current_dir.joinpath("t2.zip")
        path_t3 = current_dir.joinpath("t3.zip")
        self.assertNotEqual(hash_file(path_t1), hash_file(path_t2))
        self.assertEqual(
            hash_files_in_zip(str(path_t1)), hash_files_in_zip(str(path_t2))
        )
        self.assertNotEqual(
            hash_files_in_zip(str(path_t1)), hash_files_in_zip(str(path_t3))
        )


if __name__ == "__main__":
    main()
