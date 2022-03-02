"""
Utils.
"""
from click import echo, style

from typer.colors import RED


def error_echo(s: str) -> None:
    """

    :param s:
    :return:
    """
    echo(style(s, fg=RED), err=True)
