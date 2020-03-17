"""
Download zip.
"""
from fnmatch import fnmatch
from functools import partial
from json import load
from os import chmod, path, remove, walk
from stat import S_IRUSR, S_IWUSR
from tempfile import gettempdir
from typing import List
from zipfile import ZipFile

from requests import Session

from sharelatex_versioning.configuration import Configuration

_TMP_ZIP_FILE_NAME = "test.zip"
_GIT_IGNORE_TXT = ".gitignore"
_DEFAULT_IGNORED_FILES = [
    path.join(".git", "*"),
    ".git*",
]


def download_zip_implementation(force: bool, in_file: str, white_list: str) -> None:
    """

    Args:
        force:
        in_file:
        white_list:

    Returns:

    """
    if path.isfile(in_file):
        with open(in_file) as f_read:
            data: Configuration = load(f_read)
        zip_file_location = _download_zip_file(data["package_id"], data["share_id"])
        line_matcher = _create_line_matchers(path.basename(in_file), white_list)

        with ZipFile(zip_file_location) as zip_ref:
            name_list = set(zip_ref.namelist())

        for root, dirs, files in walk("."):
            files = (path.join(root, f) for f in files)
            files = (f for f in files if line_matcher(file_name=f[2:]))
            files = (f for f in files if f[2:] not in name_list)
            for f in files:
                _file_deletion(f, force)
        for name in (n for n in name_list if path.isfile(n)):
            chmod(name, S_IWUSR | S_IRUSR)
        with ZipFile(zip_file_location) as zip_ref:
            zip_ref.extractall(".")
        for name in name_list:
            chmod(name, S_IRUSR)
        _file_deletion(zip_file_location, True)
    else:
        print("Error: Config was empty!")


def _create_line_matchers(in_file: str, white_list: str):
    with open(_GIT_IGNORE_TXT) as f_read:
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
        print("{}: This file was removed".format(f))
    else:
        print("{}: This file should be deleted".format(f))


def _match_no_line(lines: List[str], file_name: str) -> bool:
    for current_line in lines:
        if fnmatch(file_name, current_line):
            return False
    return True
