# Copyright © Patrick Stoeckle 2020 - 2025
#
# Licensed under the Apache License License 2.0
#
# Authors: Patrick Stoeckle, Patrick Stöckle
#
# SPDX-FileCopyrightText: 2020 Patrick Stoeckle
#
# SPDX-License-Identifier: Apache-2.0

"""Stuff to clean things."""

from __future__ import annotations

from importlib.metadata import version
from logging import INFO
from logging import basicConfig
from logging import getLogger
from pathlib import Path  # noqa: TC003

from typer import Argument
from typer import Exit
from typer import Option
from typer import Typer
from typer import echo

from sharelatex_versioning.logic.download_zip import (
    download_zip_and_extract_content,
)
from sharelatex_versioning.utils.password_handling import store_password

try:
    __version__ = version("sharelatex_versioning")
except ImportError:
    __version__ = "0.0.0"

_LOGGER = getLogger(__name__)
basicConfig(
    format="%(levelname)s: %(asctime)s: %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=INFO,
    filename="sharelatex-versioning.log",
    filemode="w",
)


def _version_callback(value: bool) -> None:  # noqa: FBT001
    if value:
        echo(f"sharelatex-versioning {__version__}")
        raise Exit(0)


app = Typer(rich_markup_mode="markdown")


@app.callback()
def sharelatex_versioning(
    _1: bool = Option(  # noqa: FBT001
        None,
        "--version",
        callback=_version_callback,
        expose_value=False,
        is_eager=True,
        help="Version",
    ),
) -> None:
    """ShareLaTeX versioning tool."""


@app.command()
def download_zip(
    in_file: Path = Argument(  # noqa: B008
        ...,
        exists=True,
        dir_okay=False,
        help="The path of a JSON file containing the information of the "
        "ShareLaTeX project.",
    ),
    force: bool = Option(  # noqa: FBT001
        False,  # noqa: FBT003
        "--force",
        "-f",
        help="If this flag is passed, all the files which are not part of the "
        "ShareLaTeX project and not covered by .gitignore or the white_list "
        "option, are deleted.",
    ),
    white_list: Path | None = Option(  # noqa: B008
        None,
        "--allow-list",
        "-a",
        help="The path of a file containing all the files which"
        " are not part of the ShareLaTeX project, but should not be deleted."
        "You can use UNIX patterns.",
        exists=True,
        dir_okay=False,
    ),
    working_dir: Path = Option(  # noqa: B008
        ".",
        "--workdir",
        "-d",
        help="The path of the working dir",
        exists=True,
        file_okay=False,
    ),
) -> None:
    """Download the ShareLaTeX project and extracts the content.

    This command downloads your ShareLaTeX project as ZIP compressed file.
    Next, the zip folder is extracted into the current directory.
    All files are made readonly as the local repository should not be the place
    to edit the files.
    If you want, the script can also delete all the files which are no longer in
    your project.
    Thus, files deleted on the ShareLaTeX instance are also deleted locally.
    """
    download_zip_and_extract_content(force, in_file, white_list, working_dir)


@app.command()
def store_password_in_password_manager(
    password: str = Option(
        None,
        "--password",
        "-p",
        prompt=True,
        hide_input=True,
        help="The password for the Overleaf/ShareLaTex instance.",
    ),
    user_name: str = Option(
        None, "--username", "-u", help="The username", prompt=True
    ),
    force: bool = Option(  # noqa: FBT001
        False,  # noqa: FBT003
        "--force",
        "-f",
        help="If true, we will overwrite existing passwords.",
    ),
) -> None:
    """Store the password in the password manager."""
    store_password(force, password, user_name)


if __name__ == "__main__":
    app()
