"""
Sharelatex versioning cache.
"""

from dataclasses import asdict, dataclass
from datetime import datetime
from json import dumps, loads
from pathlib import Path
from typing import AbstractSet, Optional

CACHE_FILE = Path(".sharelatex-versioning.json")
_RUNS_TO_TRY: AbstractSet[int] = frozenset(
    [6, 12, 18, 24, 36, 48, 144, 288, 432, 576, 720, 1008, 2016, 4032]
)


@dataclass()
class Cache(object):
    """
    Help cache stored in the folder.
    """

    tries_with_same_hash: int
    old_hash: Optional[str]

    @classmethod
    def load_cache(cls) -> "Cache":
        """
        Load the cache
        Returns:

        """
        return (
            Cache(**loads(CACHE_FILE.read_text()))
            if CACHE_FILE.is_file()
            else Cache(old_hash=None, tries_with_same_hash=0)
        )

    def store(self) -> None:
        """
        Store the current cache.
        Returns:

        """
        CACHE_FILE.write_text(dumps(asdict(self)))

    def skip_this_run(self) -> bool:
        """
        To avoid DoS the server unnecessary, we only check on certain steps for new changes.
        Returns:

        """
        if self.tries_with_same_hash > 3:
            if self.tries_with_same_hash in _RUNS_TO_TRY:
                return False
            return True
        return False
