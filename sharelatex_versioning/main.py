"""
Stuff to clean things.
"""
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from sys import stdout
from typing import Any, Optional

from sharelatex_versioning import __version__
from sharelatex_versioning.logic.download_zip import download_zip_and_extract_content
from sharelatex_versioning.utils.password_handling import store_password
from typer import Exit, Option, Typer, echo

__author__ = "Patrick Stoeckle"
__copyright__ = "Patrick Stoeckle"
__license__ = "mit"

_LOGGER = getLogger(__name__)
basicConfig(
    format="%(levelname)s: %(asctime)s: %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=INFO,
    filename="sharelatex-versioning.log",
    filemode="w",
)


def _version_callback(value: bool) -> None:
    if value:
        echo(f"sharelatex-versioning {__version__}")
        raise Exit()


app = Typer()


@app.callback()
def _call_back(
    _: bool = Option(
        None,
        "--version",
        is_flag=True,
        callback=_version_callback,
        expose_value=False,
        is_eager=True,
        help="Version",
    )
) -> None:
    """

    :return:
    """


@app.command()
def download_zip(
    in_file: Path = Option(
        None,
        "--in_file",
        "-i",
        help="The path of a JSON file containing the information of the ShareLaTeX project.",
        prompt=True,
        exists=True,
        dir_okay=False,
    ),
    force: bool = Option(
        False,
        "--force",
        "-f",
        is_flag=True,
        help="If this flag is passed, all the files which are not part of the ShareLaTeX project "
        "and not covered by .gitignore or the white_list option, are deleted.",
    ),
    white_list: Optional[Path] = Option(
        None,
        "--white_list",
        "-w",
        help="The path of a file containing all the files which"
        " are not part of the ShareLaTeX project, but should not be deleted. You can use UNIX "
        "patterns.",
        exists=True,
        dir_okay=False,
    ),
    working_dir: Path = Option(
        ".",
        "--working_dir",
        "-d",
        help="The path of the working dir",
        exists=True,
        file_okay=False,
    ),
) -> None:
    """
    This command downloads your ShareLaTeX project as ZIP compressed file.
    Next, the zip folder is extracted into the current directory.
    All files are made readonly as the local repository should not be the place to edit the files.
    If you want, the script can also delete all the files which are no longer in your project.
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
        None, "--user_name", "-u", help="The username", prompt=True
    ),
    force: bool = Option(
        False,
        "--force",
        "-f",
        is_flag=True,
        help="If true, we will overwrite existing passwords.",
    ),
) -> None:
    """
    Stores the password in the password manager.
    """
    store_password(force, password, user_name)


if __name__ == "__main__":
    app()
