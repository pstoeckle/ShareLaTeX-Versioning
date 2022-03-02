"""
Download zip.
"""
from fnmatch import fnmatch
from functools import partial
from json import dumps, loads
from json.decoder import JSONDecodeError
from logging import getLogger
from os import chmod, remove, walk
from os.path import basename, isfile, join
from os.path import sep as path_sep
from pathlib import Path
from stat import S_IRUSR, S_IWUSR
from subprocess import call
from tempfile import gettempdir
from typing import Callable, List, Optional
from zipfile import ZipFile

from bs4 import BeautifulSoup
from requests import Session

from sharelatex_versioning.classes.cache import CACHE_FILE, Cache
from sharelatex_versioning.classes.configuration import Configuration
from sharelatex_versioning.logic.hash_file import are_there_new_changes
from sharelatex_versioning.utils import error_echo
from sharelatex_versioning.utils.password_handling import get_password_from_keyring
from typer import Exit, echo

_LOGGER = getLogger(__name__)


_TMP_ZIP_FILE_NAME = "test.zip"
_GIT_IGNORE_TXT = ".gitignore"
_DEFAULT_IGNORED_FILES = [join(".git", "*"), ".git*", ".sharelatex_versioning"]


def download_zip_and_extract_content(
    force: bool, in_file: Path, white_list: Optional[Path], working_dir: Path
) -> None:
    """

    Args:
        working_dir:
        force:
        in_file:
        white_list:

    Returns:

    """
    work_dir_replacer = partial(_replace_workdir, workdir=str(working_dir))
    data: Configuration = Configuration(**loads(in_file.read_text()))
    cache = (
        Cache(**loads(CACHE_FILE.read_text()))
        if CACHE_FILE.is_file()
        else Cache(old_hash=None, tries_with_same_hash=0)
    )
    if cache.skip_this_run():
        cache.tries_with_same_hash += 1
        cache.store()
        echo("We skip this run to avoid to DoS the server")
        raise Exit()
    echo("Start download...")
    zip_file_location = _download_zip_file(data)
    if zip_file_location is None:
        error_echo("Aborting! There is no ZIP file.")
        raise Exit(1)
    echo("Download done!")
    if not are_there_new_changes(zip_file_location, cache):
        cache.tries_with_same_hash += 1
        cache.store()
        remove(zip_file_location)
        echo(
            f"After hashing all files of the new zip, we got the same hash ({cache.old_hash}) as for the last zip. No new changes..."
        )
        raise Exit()
    else:
        cache.tries_with_same_hash = 0
        cache.store()
    line_matcher = _create_line_matchers(in_file.name, white_list, str(working_dir))
    echo("Starting unzipping ...")
    with ZipFile(zip_file_location) as zip_ref:
        name_list = set(zip_ref.namelist())
        for f in sorted(name_list):
            _LOGGER.info(f"File ZIP: {f}")
    for root, dirs, files in walk(working_dir):
        files = list(join(root, f) for f in files)
        files = list(
            f for f in files if line_matcher(file_name=work_dir_replacer(file_name=f))
        )
        files = list(
            f for f in files if work_dir_replacer(file_name=f) not in name_list
        )
        for f in files:
            _file_deletion(f, force)
    full_name_list = [join(working_dir, n) for n in name_list]
    for name in (n for n in full_name_list if isfile(n)):
        chmod(name, S_IWUSR | S_IRUSR)
    with ZipFile(zip_file_location) as zip_ref:
        zip_ref.extractall(working_dir)
    for name in full_name_list:
        chmod(name, S_IRUSR)
        _LOGGER.info(f"git add {name}")
        call(["git", "add", name], cwd=working_dir)
    _file_deletion(str(zip_file_location), True)
    echo("Unzipping done!")


def _replace_workdir(file_name: str, workdir: str) -> str:
    if file_name.startswith(workdir):
        return file_name.replace(workdir, "", 1).lstrip(path_sep)
    else:
        return file_name


def _create_line_matchers(
    in_file: str, white_list: Optional[Path], working_dir: str
) -> Callable[..., bool]:
    git_ignore_path = Path(join(working_dir, _GIT_IGNORE_TXT))
    if git_ignore_path.is_file():
        with git_ignore_path.open() as f_read:
            lines = f_read.readlines()
    else:
        lines = []
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
        lines.append(basename(white_list))
        with open(white_list) as f_read:
            white_list_entries = f_read.readlines()
        for white_list_entry in white_list_entries:
            lines.append(white_list_entry.strip())
    line_matcher = partial(_match_no_line, lines=lines)
    return line_matcher


def _join_url(parts: List[str]) -> str:
    return "/".join([p.strip("/") for p in parts])


def _download_zip_file(configuration: Configuration) -> Optional[Path]:
    """

    Args:
        configuration:

    Returns:

    """

    s = Session()
    login_url = _join_url([configuration.sharelatex_url, "ldap/login"])
    r = s.get(login_url, allow_redirects=True)
    user_name = configuration.username
    password = get_password_from_keyring(user_name)
    if password is None:
        return None
    if r.status_code == 200:
        csrf = BeautifulSoup(r.text, "html.parser").find("input", {"name": "_csrf"})[
            "value"
        ]

        r2 = s.post(
            login_url,
            data={
                "_csrf": csrf,
                "login": user_name,
                "password": password,
            },
        )
        message = None
        try:
            message = loads(r2.text)
        except JSONDecodeError:
            _LOGGER.debug("Message is not JSON")
            _LOGGER.debug(r2.text)
        if r2.status_code == 200 and message is None:
            download_path = _join_url(
                [
                    configuration.sharelatex_url,
                    "project",
                    configuration.project_id,
                    "download/zip",
                ]
            )
            r3 = s.get(download_path, allow_redirects=True)
            if r3.status_code == 200:
                tmp_path = join(gettempdir(), _TMP_ZIP_FILE_NAME)
                open(tmp_path, "wb").write(r3.content)
                return Path(tmp_path)
            else:
                _LOGGER.critical("Could not download the ZIP")
                _LOGGER.critical(r3.text)

        else:
            _LOGGER.critical("Authentication failed!")
            _LOGGER.critical(dumps(message))
    return None


def _file_deletion(f: str, force: bool) -> None:
    if force:
        remove(f)
        _LOGGER.info(f"{f}: This file was removed")
    else:
        _LOGGER.info(f"{f}: This file should be deleted")


def _match_no_line(lines: List[str], file_name: str) -> bool:
    for current_line in lines:
        if fnmatch(file_name, current_line):
            return False
    return True
