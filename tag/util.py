import os.path
import glob
from .error import TagException

import urllib.parse


def split_version(version_string, num_parts):
    """Given a version string, splits it into a ``num_parts``-length tuple. If the string has too many or too few parts, an error is raised."""
    splitver = version_string.split(".")
    if len(splitver) != num_parts:
        raise Exception("invalid version: " + version_string)
    return tuple(splitver)


def try_resolve_db(base_path="."):
    """Looks in the directory ``base_path`` for any SQLite databases that
    follow the ``*.tag.sqlite`` naming convention.
    If we find exactly one, return it.
    If we find too many, an exception is raised so the user can resolve the ambiguity
    If we don't find any, the parent directory is checked with these same rules, until we
    either find a database or bottom out the filesystem.
    """
    rel_path = base_path
    glob_pattern = "*.tag.sqlite"
    while True:

        glob_path = os.path.join(glob.escape(rel_path), glob_pattern)

        resolved_dbs = glob.glob(glob_path)

        if len(resolved_dbs) > 1:
            raise TagException(
                "Cannot decide which *.tag.sqlite file to use. Found multiple files ("
                + ", ".join(map(os.path.basename, resolved_dbs))
                + ') in the folder: "'
                + os.path.abspath(rel_path)
                + '". Please specify which file to use with the --database flag.'
            )

        if len(resolved_dbs) == 1:
            return os.path.relpath(resolved_dbs[0])

        rel_path = os.path.join("..", rel_path)
        if not os.path.isdir(rel_path):
            return None


def path_to_uri(path, host=None):
    return 'file://{}/{}'.format(urllib.parse.quote(host or ''), urllib.parse.quote(os.path.abspath(path)))

def uri_to_path(uri):
    parsed_uri = urllib.parse.urlparse(uri)
    if parsed_uri.scheme != 'file':
        raise TagException('Unsupported uri scheme: ' + parsed_uri.scheme)
    host = urllib.parse.unquote(parsed_uri.netloc)
    path = urllib.parse.unquote(os.path.relpath(parsed_uri.path))
    return (path, host)