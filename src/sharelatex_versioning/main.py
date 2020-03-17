"""
Stuff to clean things.
"""
from os import path
from typing import Optional

from click import group, option
from pandas import read_csv

from sharelatex_versioning.download_zip import download_zip_implementation

__author__ = "Patrick Stoeckle"
__copyright__ = "Patrick Stoeckle"
__license__ = "mit"


_IN_FILE_OPTION = option(
    "--in_file",
    "-i",
    default="",
    help="The path of a JSON file containing the information of the ShareLaTeX project.",
)
_WHITE_LIST_OPTION = option(
    "--white_list",
    "-w",
    default=None,
    help="The path of a file containing all the files which"
    " are not part of the ShareLaTeX project, but should not be deleted. You can use UNIX "
    "patterns.",
)
_FORCE_OPTION = option(
    "--force",
    "-f",
    is_flag=True,
    default=False,
    help="If this flag is passed, all the files which are not part of the ShareLaTeX project "
    "and not convered by .gitignore or the white_list option, are deleted.",
)


@group()
def main_group() -> None:
    """

    :return:
    """


@_IN_FILE_OPTION
@main_group.command(name="convert_csv")
def _convert_csv_entry(in_file: str) -> None:
    """

    :return:
    """
    if path.isfile(in_file):
        data = read_csv(in_file)
        for key in ["oncleanper", "afterapplicationper", "deltaper", "missingrulesper"]:
            data[key] *= 100
        data = data.round(1)
        data.to_csv(in_file, sep=";")


@_WHITE_LIST_OPTION
@_IN_FILE_OPTION
@_FORCE_OPTION
@main_group.command()
def download_zip(in_file: str, force: bool, white_list: Optional[str]) -> None:
    """
    This command downloads your ShareLaTeX project as ZIP compressed file.
    Next, the zip folder is extracted into the current directory.
    All files are made readonly as the local repository should not be the place to edit the files.
    If you want, the script can also delete all the files which are no longer in your project.
    Thus, files deleted on the ShareLaTeX instance are also deleted locally.
    """
    download_zip_implementation(force, in_file, white_list)


if __name__ == "__main__":
    main_group()
