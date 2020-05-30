

import re
import os.path
from contextlib import contextmanager
from collections import namedtuple
from datetime import datetime


from .mimetypes import guess_mime_type

__version__ = "0.0.1"

from .version import version, version_info
from .connection import connect
from .crud import get, insert, update, upsert, delete
from .ingest import ingest_file