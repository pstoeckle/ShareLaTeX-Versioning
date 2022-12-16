"""
Class.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Configuration(object):
    """
    Class.
    """

    project_id: str
    username: str
    sharelatex_url: str = "https://sharelatex.tum.de/"
