"""
Class.
"""
import sys

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict


class Configuration(TypedDict):
    """
    Class.
    """

    project_id: str
    username: str
    password: str
    sharelatex_url: str
