"""
Hash file.
"""
from hashlib import sha3_256
from logging import getLogger
from pathlib import Path
from typing import Optional
from zipfile import ZipFile

from sharelatex_versioning.classes.cache import Cache
from typer import echo

_LOGGER = getLogger(__name__)


def hash_file(file_name: Path) -> str:
    """

    :param file_name:
    :return:
    """
    if not file_name.is_file():
        return ""
    current_sha = sha3_256()
    with file_name.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            current_sha.update(chunk)
    return current_sha.hexdigest()


def hash_files_in_zip(zip_file: str) -> str:
    """

    Args:
        zip_file:

    Returns:

    """
    current_sha = sha3_256()
    with ZipFile(zip_file) as zip_ref:
        for name in zip_ref.namelist():
            with zip_ref.open(name) as current_file:
                for chunk in iter(lambda: current_file.read(4096), b""):
                    current_sha.update(chunk)
    hexdigest = current_sha.hexdigest()
    _LOGGER.info(f"File {zip_file} -> {hexdigest}")
    return hexdigest


def are_there_new_changes(zip_file_location: Path, cache: Cache) -> bool:
    """

    Args:
        zip_file_location:
        cache:

    Returns:

    """
    current_hash = hash_files_in_zip(str(zip_file_location))
    if cache.old_hash is not None and current_hash == cache.old_hash:
        return False
    else:
        cache.old_hash = current_hash
        return True
