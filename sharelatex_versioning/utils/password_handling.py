"""
Password handling
"""
from logging import getLogger
from sys import platform
from typing import Optional

from keyring import get_password, set_keyring, set_password
from keyring.backends.macOS import Keyring as macos_Keyring
from keyring.backends.Windows import WinVaultKeyring

SERVICE_NAME = "sharelatex-versioning"

_LOGGER = getLogger(__file__)


def store_password(force: bool, password: str, user_name: str) -> None:
    """

    :param force:
    :param password:
    :param user_name:
    :return:
    """
    if platform == "linux" or platform == "linux2":
        _LOGGER.critical("Please configure the right keyring!!!")
    elif platform == "darwin":
        set_keyring(macos_Keyring())
    elif platform == "win32":
        set_keyring(WinVaultKeyring())
    current_password = get_password(SERVICE_NAME, user_name)
    if current_password is not None:
        _LOGGER.warning(f"There is already a password stored for {user_name}")
        if not force:
            return
    set_password(SERVICE_NAME, user_name, password)
    _LOGGER.info("We stored the password!")


def get_password_from_keyring(user_name: str) -> Optional[str]:
    """

    :param user_name:
    :return:
    """
    p = get_password(SERVICE_NAME, user_name)
    if p is None:
        _LOGGER.critical(f"No password stored for {user_name}")
    return p
