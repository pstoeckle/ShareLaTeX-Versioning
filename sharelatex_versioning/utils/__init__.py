# Copyright © Patrick Stoeckle 2020 - 2025
#
# Licensed under the Apache License License 2.0
#
# Authors: Patrick Stoeckle, Patrick Stöckle
#
# SPDX-FileCopyrightText: 2020 Patrick Stoeckle
#
# SPDX-License-Identifier: Apache-2.0

"""Utils."""

from __future__ import annotations

from click import echo
from click import style
from typer.colors import RED


def error_echo(s: str) -> None:
    """Echo an error message in red."""
    echo(style(s, fg=RED), err=True)


HTML_OK_CODE = 200
