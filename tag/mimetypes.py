import os.path
import mimetypes


default_extensions = {
    "sqlite": "application/vnd.sqlite3",
}

default_extensions.update(
    {x: "application/octet-stream" for x in ["exe", "msi", "bin", "o",]}
)
default_extensions.update({x: "text/plain" for x in ["md", "rst"]})


def guess_mime_type(filename, default_type="text/plain", extensions=default_extensions):
    """ Tries to guess the MIME type of a file.

    1. If the file's extension matches a key in the ``extensions`` parameter, the associated value is returned.
    2. Next, the Python mimetypes module is given a chance to guess the mime type.
    3. If nobody knows the mime type, the ``default_type`` is returned.
    """

    basename = os.path.basename(filename)
    ext = os.path.splitext(basename)[1]

    # First, if we know the mime type already, just return it.
    if ext in extensions:
        print(extensions, ext, extensions[ext])
        return extensions[ext]

    # If we don't know it, give python mimetypes module a chance to guess it
    py_guess = mimetypes.guess_type(filename)[0]
    if py_guess:
        return py_guess

    # If they don't know it either, just return the default.
    return default_type
