# Copyright © Patrick Stoeckle 2020 - 2025
#
# Licensed under the Apache License License 2.0
#
# Authors: Patrick Stoeckle, Patrick Stöckle
#
# SPDX-FileCopyrightText: 2020 Patrick Stoeckle
#
# SPDX-License-Identifier: Apache-2.0

"""Password handling."""

from __future__ import annotations

from sys import platform

from keyring import get_password
from keyring import set_keyring
from keyring import set_password
from keyring.backends.macOS import Keyring as macos_Keyring
from keyring.backends.Windows import WinVaultKeyring
from typer import Exit
from typer import echo

from sharelatex_versioning.utils import error_echo

SERVICE_NAME = "sharelatex-versioning"


def store_password(force: bool, password: str, user_name: str) -> None:  # noqa: FBT001
    """Store the password in the keyring."""
    _set_keyring()
    current_password = get_password(SERVICE_NAME, user_name)
    if current_password is not None:
        echo(f"There is already a password stored for {user_name}")
        if not force:
            return
    set_password(SERVICE_NAME, user_name, password)
    echo("We stored the password!")


def get_password_from_keyring(user_name: str) -> str | None:
    """Get password from keyring."""
    _set_keyring()
    p = get_password(SERVICE_NAME, user_name)
    if p is None:
        error_echo(f"No password stored for {user_name}")
        raise Exit(1)
    return p


def _set_keyring() -> None:
    if platform == "linux" or platform == "linux2":
        error_echo("Please configure the right keyring!!!")
    elif platform == "darwin":
        set_keyring(macos_Keyring())
    elif platform == "win32":
        set_keyring(WinVaultKeyring())
