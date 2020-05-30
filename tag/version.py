import sys
from sqlite3 import sqlite_version

from . import __version__

def version():
    """Returns a human-readable version string."""
    return "{} (python {}; sqlite driver {})".format(
        __version__, "{}.{}.{}".format(*sys.version_info[0:3]), sqlite_version
    )

def version_info():
    """Returns a tuple representation of the version, with three numbers: (major, minor, patch)."""
    return map(int, __version__.split("."))