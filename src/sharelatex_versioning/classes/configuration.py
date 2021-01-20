"""
Class.
"""
try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


class Configuration(TypedDict):
    """
    Class.
    """

    project_id: str
    username: str
    password: str
    sharelatex_url: str
