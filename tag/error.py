# TODO -- wrap click with error handling so we can stop inheriting from ClickException
from click import ClickException


class TagException(ClickException):
    """Defines an application-layer exception that can be shown to the user."""

    pass
