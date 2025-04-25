# Copyright © Patrick Stoeckle 2020 - 2025
#
# Licensed under the Apache License License 2.0
#
# Authors: Patrick Stoeckle, Patrick Stöckle
#
# SPDX-FileCopyrightText: 2020 Patrick Stoeckle
#
# SPDX-License-Identifier: Apache-2.0

"""Hash file handling."""

from __future__ import annotations

from hashlib import sha3_256
from logging import getLogger
from typing import TYPE_CHECKING
from zipfile import ZipFile

if TYPE_CHECKING:
    from pathlib import Path

    from sharelatex_versioning.classes.cache import Cache

_LOGGER = getLogger(__name__)


def hash_file(file_name: Path) -> str:
    """Hash a file."""
    if not file_name.is_file():
        return ""
    current_sha = sha3_256()
    with file_name.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            current_sha.update(chunk)
    return current_sha.hexdigest()


def hash_files_in_zip(zip_file: str) -> str:
    """Hash files in ZIP."""
    current_sha = sha3_256()
    with ZipFile(zip_file) as zip_ref:
        for name in zip_ref.namelist():
            with zip_ref.open(name) as current_file:
                for chunk in iter(lambda: current_file.read(4096), b""):
                    current_sha.update(chunk)
    hexdigest = current_sha.hexdigest()
    msg = f"File {zip_file} -> {hexdigest}"
    _LOGGER.info(msg)
    return hexdigest


def are_there_new_changes(zip_file_location: Path, cache: Cache) -> bool:
    """Check if there are new changes in the ZIP file."""
    current_hash = hash_files_in_zip(str(zip_file_location))
    if cache.old_hash is not None and current_hash == cache.old_hash:
        return False
    cache.old_hash = current_hash
    return True
