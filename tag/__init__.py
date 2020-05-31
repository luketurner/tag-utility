__version__ = "0.0.1"

from .version import version, version_info
from .connection import connect
from .crud import get, insert, update, upsert, delete
from .ingest import ingest_file
from .search import search