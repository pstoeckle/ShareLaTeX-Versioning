"""
Download zip.
"""
from fnmatch import fnmatch
from functools import partial
from hashlib import sha1
from json import load
from logging import INFO, basicConfig, getLogger
from os import chmod, path, remove, sep, walk
from os.path import isfile, join
from stat import S_IRUSR, S_IWUSR
from subprocess import call
from tempfile import gettempdir
from typing import List, Optional
from zipfile import ZipFile

from requests import Session

from sharelatex_versioning.configuration import Configuration

basicConfig(
    level=INFO,
    format="%(asctime)s-%(levelname)s: %(message)s",
    datefmt="%Y_%m_%d %H:%M",
)
_LOGGER = getLogger(__name__)


_TMP_ZIP_FILE_NAME = "test.zip"
_GIT_IGNORE_TXT = ".gitignore"
_DEFAULT_IGNORED_FILES = [
    path.join(".git", "*"),
    ".git*",
]


def download_zip_implementation(
    force: bool, in_file: str, white_list: str, working_dir: str
) -> None:
    """

    Args:
        working_dir:
        force:
        in_file:
        white_list:

    Returns:

    """
    if path.isfile(in_file):
        working_dir = working_dir.rstrip(sep)
        work_dir_replacer = partial(_replace_workdir, workdir=working_dir)
        with open(in_file) as f_read:
            data: Configuration = load(f_read)
        zip_file_location = _download_zip_file(data["project_id"], data["share_id"])
        if not _are_there_new_changes(working_dir, zip_file_location):
            remove(zip_file_location)
            return
        line_matcher = _create_line_matchers(
            path.basename(in_file), white_list, working_dir
        )

        with ZipFile(zip_file_location) as zip_ref:
            name_list = set(zip_ref.namelist())
        for root, dirs, files in walk(working_dir):
            files = (path.join(root, f) for f in files)
            files = (
                f
                for f in files
                if line_matcher(file_name=work_dir_replacer(file_name=f))
            )
            files = (
                f for f in files if work_dir_replacer(file_name=f) not in name_list
            )
            for f in files:
                _file_deletion(f, force)
        full_name_list = [path.join(working_dir, n) for n in name_list]
        for name in (n for n in full_name_list if path.isfile(n)):
            chmod(name, S_IWUSR | S_IRUSR)
        with ZipFile(zip_file_location) as zip_ref:
            zip_ref.extractall(working_dir)
        for name in full_name_list:
            chmod(name, S_IRUSR)
            call(["git", "add", name], cwd=working_dir)
        _file_deletion(zip_file_location, True)
    else:
        _LOGGER.critical("Error: Config was empty!")


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


def _are_there_new_changes(working_dir: str, zip_file_location: str) -> bool:
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


def _replace_workdir(file_name: str, workdir: str) -> str:
    return file_name.replace(workdir, "")[1:]


def _create_line_matchers(in_file: str, white_list: str, working_dir: str):
    with open(path.join(working_dir, _GIT_IGNORE_TXT)) as f_read:
        lines = f_read.readlines()
    lines = list(
        [
            current_line.strip()
            for current_line in lines
            if not current_line.startswith("#") and current_line.strip() != ""
        ]
        + _DEFAULT_IGNORED_FILES
        + [in_file]
    )
    if white_list is not None:
        lines.append(path.basename(white_list))
        with open(white_list) as f_read:
            white_list_entries = f_read.readlines()
        for white_list_entry in white_list_entries:
            lines.append(white_list_entry.strip())
    line_matcher = partial(_match_no_line, lines=lines)
    return line_matcher


def _download_zip_file(package_id: str, share_id: str) -> str:
    """

    """
    s = Session()
    s.get(path.join("https://sharelatex.tum.de/read", share_id), allow_redirects=True)
    r = s.get(
        path.join("https://sharelatex.tum.de/project", package_id, "download/zip"),
        allow_redirects=True,
    )
    tmp_path = path.join(gettempdir(), _TMP_ZIP_FILE_NAME)
    open(tmp_path, "wb").write(r.content)
    return tmp_path


def _file_deletion(f: str, force: bool) -> None:
    if force:
        remove(f)
        _LOGGER.info("{}: This file was removed".format(f))
    else:
        _LOGGER.info("{}: This file should be deleted".format(f))


def _match_no_line(lines: List[str], file_name: str) -> bool:
    for current_line in lines:
        if fnmatch(file_name, current_line):
            return False
    return True
