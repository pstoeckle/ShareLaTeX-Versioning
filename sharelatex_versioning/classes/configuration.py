# Copyright © Patrick Stoeckle 2020 - 2025
#
# Licensed under the Apache License License 2.0
#
# Authors: Patrick Stoeckle, Patrick Stöckle
#
# SPDX-FileCopyrightText: 2020 Patrick Stoeckle
#
# SPDX-License-Identifier: Apache-2.0

"""Class."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Configuration:
    """Configuration class."""

    project_id: str
    username: str
    sharelatex_url: str = "https://sharelatex.tum.de/"
