"""
Stuff to clean things.
"""
from logging import INFO, basicConfig, getLogger
from sys import stdout
from typing import Optional

from click import group, option

from sharelatex_versioning import __version__
from sharelatex_versioning.logic.download_zip import download_zip_and_extract_content

__author__ = "Patrick Stoeckle"
__copyright__ = "Patrick Stoeckle"
__license__ = "mit"

_LOGGER = getLogger(__name__)
basicConfig(
    format="%(levelname)s: %(asctime)s: %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=INFO,
    stream=stdout,
)


@group()
def main_group() -> None:
    """

    :return:
    """


@option(
    "--working_dir",
    "-d",
    default=".",
    help="The path of the working dir",
)
@option(
    "--white_list",
    "-w",
    default=None,
    help="The path of a file containing all the files which"
    " are not part of the ShareLaTeX project, but should not be deleted. You can use UNIX "
    "patterns.",
)
@option(
    "--in_file",
    "-i",
    default="",
    help="The path of a JSON file containing the information of the ShareLaTeX project.",
)
@option(
    "--force",
    "-f",
    is_flag=True,
    default=False,
    help="If this flag is passed, all the files which are not part of the ShareLaTeX project "
    "and not covered by .gitignore or the white_list option, are deleted.",
)
@main_group.command()
def download_zip(
    in_file: str,
    force: bool,
    white_list: Optional[str],
    working_dir: str,
) -> None:
    """
    This command downloads your ShareLaTeX project as ZIP compressed file.
    Next, the zip folder is extracted into the current directory.
    All files are made readonly as the local repository should not be the place to edit the files.
    If you want, the script can also delete all the files which are no longer in your project.
    Thus, files deleted on the ShareLaTeX instance are also deleted locally.
    """
    _print_version()
    download_zip_and_extract_content(force, in_file, white_list, working_dir)


@main_group.command()
def version():
    """

    :return:
    """
    _print_version()


def _print_version() -> None:
    _LOGGER.info(f"sharelatex-versioning {__version__}")


if __name__ == "__main__":
    main_group()
