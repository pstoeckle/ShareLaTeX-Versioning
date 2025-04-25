# Copyright © Patrick Stoeckle 2021 - 2025
#
# Licensed under the Apache License License 2.0
#
# Authors: Patrick Stoeckle, Patrick Stöckle
#
# SPDX-FileCopyrightText: 2021 Patrick Stoeckle
#
# SPDX-License-Identifier: Apache-2.0

"""Sharelatex versioning cache."""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from json import dumps
from json import loads
from pathlib import Path

CACHE_FILE = Path(".sharelatex-versioning.json")
_RUNS_TO_TRY: set[int] = {
    6,
    12,
    18,
    24,
    36,
    48,
    144,
    288,
    432,
    576,
    720,
    1008,
    2016,
    4032,
}

_MAX_TRIES = 3


@dataclass()
class Cache:
    """Help cache stored in the folder."""

    tries_with_same_hash: int
    old_hash: str | None

    @classmethod
    def load_cache(cls) -> Cache:
        """Load the cache."""
        return (
            Cache(**loads(CACHE_FILE.read_text()))
            if CACHE_FILE.is_file()
            else Cache(old_hash=None, tries_with_same_hash=0)
        )

    def store(self) -> None:
        """Store the current cache."""
        CACHE_FILE.write_text(dumps(asdict(self)))

    def skip_this_run(self) -> bool:
        """Skip this run.

        To avoid DoS the server unnecessary, we only check on certain steps for
        new changes.
        """
        if self.tries_with_same_hash > _MAX_TRIES:
            return self.tries_with_same_hash not in _RUNS_TO_TRY
        return False
