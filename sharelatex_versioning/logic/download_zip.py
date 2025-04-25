# Copyright © Patrick Stoeckle 2020 - 2025
#
# Licensed under the Apache License License 2.0
#
# Authors: Patrick Stoeckle, Patrick Stöckle
#
# SPDX-FileCopyrightText: 2020 Patrick Stoeckle
#
# SPDX-License-Identifier: Apache-2.0

"""Download the ZIP file from Sharelatex and extract the content."""

from __future__ import annotations

from fnmatch import fnmatch
from functools import partial
from json import dumps
from json import loads
from json.decoder import JSONDecodeError
from logging import getLogger
from os import walk
from os.path import sep as path_sep
from pathlib import Path
from stat import S_IRUSR
from stat import S_IWUSR
from subprocess import call
from tempfile import gettempdir
from typing import TYPE_CHECKING
from zipfile import ZipFile

from bs4 import BeautifulSoup
from requests import Session
from typer import Exit
from typer import echo

from sharelatex_versioning.classes.cache import CACHE_FILE
from sharelatex_versioning.classes.cache import Cache
from sharelatex_versioning.classes.configuration import Configuration
from sharelatex_versioning.logic.hash_file import are_there_new_changes
from sharelatex_versioning.utils import HTML_OK_CODE
from sharelatex_versioning.utils import error_echo
from sharelatex_versioning.utils.password_handling import (
    get_password_from_keyring,
)

if TYPE_CHECKING:
    from collections.abc import Callable

_LOGGER = getLogger(__name__)


_TMP_ZIP_FILE_NAME = "test.zip"
_GIT_IGNORE_TXT = ".gitignore"
_DEFAULT_IGNORED_FILES = [".git/*", ".git*", ".sharelatex_versioning"]


def download_zip_and_extract_content(
    force: bool,  # noqa: FBT001
    in_file: Path,
    white_list: Path | None,
    working_dir: Path,
) -> None:
    """Download the ZIP file from Sharelatex and extract the content."""
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
        raise Exit(0)
    echo("Start download...")
    zip_file_location = _download_zip_file(data)
    if zip_file_location is None:
        error_echo("Aborting! There is no ZIP file.")
        raise Exit(1)
    echo("Download done!")
    if not are_there_new_changes(zip_file_location, cache):
        cache.tries_with_same_hash += 1
        cache.store()
        zip_file_location.unlink()
        echo(
            "After hashing all files of the new zip, we got the same hash "
            f"({cache.old_hash}) as for the last zip. No new changes..."
        )
        raise Exit(0)
    cache.tries_with_same_hash = 0
    cache.store()
    line_matcher = _create_line_matchers(
        in_file.name, white_list, str(working_dir)
    )
    echo("Starting unzipping ...")
    with ZipFile(zip_file_location) as zip_ref:
        name_list = set(zip_ref.namelist())
        for f in sorted(name_list):
            msg = f"File ZIP: {f}"
            _LOGGER.info(msg)
    for root, _dirs, files in walk(working_dir):
        c_files = [str(Path(root).joinpath(f)) for f in files]
        after_files = [
            f
            for f in c_files
            if line_matcher(file_name=work_dir_replacer(file_name=f))
        ]
        after_after_files = [
            f
            for f in after_files
            if work_dir_replacer(file_name=f) not in name_list
        ]
        for f in after_after_files:
            _file_deletion(f, force)
    full_name_list = [working_dir.joinpath(n) for n in name_list]
    for name in (n for n in full_name_list if n.is_file()):
        name.chmod(S_IWUSR | S_IRUSR)
    with ZipFile(zip_file_location) as zip_ref:
        zip_ref.extractall(working_dir)
    for name in full_name_list:
        name.chmod(S_IRUSR)
        msg = f"git add {name}"
        _LOGGER.info(msg)
        call(["git", "add", name], cwd=working_dir)  # noqa: S603, S607
    _file_deletion(str(zip_file_location), True)  # noqa: FBT003
    echo("Unzipping done!")


def _replace_workdir(file_name: str, workdir: str) -> str:
    if file_name.startswith(workdir):
        return file_name.replace(workdir, "", 1).lstrip(path_sep)
    return file_name


def _create_line_matchers(
    in_file: str, white_list: Path | None, working_dir: str
) -> Callable[..., bool]:
    git_ignore_path = Path(working_dir).joinpath(_GIT_IGNORE_TXT)
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
        lines.append(white_list.name)
        with white_list.open() as f_read:
            white_list_entries = f_read.readlines()
        for white_list_entry in white_list_entries:
            lines.append(white_list_entry.strip())
    return partial(_match_no_line, lines=lines)


def _join_url(parts: list[str]) -> str:
    return "/".join([p.strip("/") for p in parts])


def _download_zip_file(configuration: Configuration) -> Path | None:
    """Down load the ZIP file from Sharelatex."""
    s = Session()
    login_url = _join_url([configuration.sharelatex_url, "ldap/login"])
    r = s.get(login_url, allow_redirects=True)
    user_name = configuration.username
    password = get_password_from_keyring(user_name)
    if password is None:
        return None
    if r.status_code == HTML_OK_CODE:
        csrf = BeautifulSoup(r.text, "html.parser").find(  # type: ignore[index]
            "input", {"name": "_csrf"}
        )["value"]

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
        if r2.status_code == HTML_OK_CODE and message is None:
            download_path = _join_url(
                [
                    configuration.sharelatex_url,
                    "project",
                    configuration.project_id,
                    "download/zip",
                ]
            )
            r3 = s.get(download_path, allow_redirects=True)
            if r3.status_code == HTML_OK_CODE:
                tmp_path = Path(gettempdir()).joinpath(_TMP_ZIP_FILE_NAME)
                with tmp_path.open("wb") as f:
                    f.write(r3.content)
                return Path(tmp_path)
            _LOGGER.critical("Could not download the ZIP")
            _LOGGER.critical(r3.text)

        else:
            _LOGGER.critical("Authentication failed!")
            _LOGGER.critical(dumps(message))
    return None


def _file_deletion(f: str, force: bool) -> None:  # noqa: FBT001
    if force:
        Path(f).unlink()
        msg = f"{f}: This file was removed"
    else:
        msg = f"{f}: This file should be deleted"
    _LOGGER.info(msg)


def _match_no_line(lines: list[str], file_name: str) -> bool:
    return all(not fnmatch(file_name, current_line) for current_line in lines)
