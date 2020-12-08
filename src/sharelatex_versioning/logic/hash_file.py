"""
Hash file.
"""
from hashlib import sha1
from logging import getLogger
from os.path import isfile, join
from typing import Optional
from zipfile import ZipFile

_LOGGER = getLogger(__name__)


def hash_file(file_name: str) -> str:
    """

    :param file_name:
    :return:
    """
    if not isfile(file_name):
        return ""
    current_sha = sha1()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            current_sha.update(chunk)
    return current_sha.hexdigest()


def hash_files_in_zip(zip_file: str) -> str:
    """

    Args:
        zip_file:

    Returns:

    """
    current_sha = sha1()
    with ZipFile(zip_file) as zip_ref:
        for name in zip_ref.namelist():
            with zip_ref.open(name) as current_file:
                for chunk in iter(lambda: current_file.read(4096), b""):
                    current_sha.update(chunk)
    hexdigest = current_sha.hexdigest()
    _LOGGER.info(f"File {zip_file} -> {hexdigest}")
    return hexdigest


def are_there_new_changes(working_dir: str, zip_file_location: str) -> bool:
    """

    Args:
        working_dir:
        zip_file_location:

    Returns:

    """
    last_hash_file = join(working_dir, ".sharelatex_versioning")
    last_hash: Optional[str] = None
    if isfile(last_hash_file):
        with open(last_hash_file) as f_read:
            last_hash = f_read.read().strip()
    current_hash = hash_files_in_zip(zip_file_location)
    if last_hash is not None and current_hash == last_hash:
        _LOGGER.info(
            f"After hashing all files of the new zip, we got the same hash ({current_hash}) as for the last zip. No new changes..."
        )
        return False
    else:
        with open(last_hash_file, "w") as f_write:
            f_write.write(current_hash)
    return True
