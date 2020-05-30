import os.path

from .crud import upsert
from .mimetypes import guess_mime_type

def ingest_file(conn, filename, tags=None):
  """Ingests a single file, retaining as much metadata about the file as possible.

    The file is stored with a ``file:///`` URI, and mimetype guessed according to the Python mimetypes library.
    If an existing file already has this URI, it will be updated instead of creating a new one.

    Accepts ``tags`` parameter that can optionally specify a dictionary of tags to apply to the ingested file.
    The dictionary keys should be tag names, and the values should be the desired value for the file_tag, or None if no value is desired.
    If a tag in the tags dict can't be found, it will be created automatically.
    """
    abs_name = os.path.abspath(filename)
    _assert_file(abs_name)
    file = upsert(conn, conn.File,
      uri="file://" + abs_name,
      mime_type=guess_mime_type(abs_name),
      name=os.path.basename(abs_name),
    )

    for name, value in (tags or {}).items():
      tag = upsert(conn, conn.Tag, name=name)
      file_tag = upsert(conn, conn.FileTag, file=file, tag=tag, value=value)

    return file


def _assert_file(filename):
    if not os.path.isfile(filename):
        raise Exception('"{}" is not a file'.format((abs_name,)))
