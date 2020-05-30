import re
from datetime import datetime

from pony.orm import *
from pony.orm.core import TransactionIntegrityError, CacheIndexError

def get(conn, model, id):
  return select(x for x in model if x.id == id).first()


def insert(conn, model, **kwargs):
  instance = model(
    **{ k: v for k, v in kwargs.items() if v != None },
    created_at = kwargs.get("created_at", datetime.now()),
    updated_at = kwargs.get("updated_at", datetime.now()),
  )
  commit()
  return instance


def update(conn, model, update_key='id', **kwargs):
  # TODO - special case logic to handle update on composite primary key
  if model == "FileTag" or model.__name__ == "FileTag":
    existing = select(x for x in model if x.file == kwargs.get('file') and x.tag == kwargs.get('tag')).first()
  else:
    existing = select(x for x in model if getattr(x, update_key) == kwargs.get(update_key)).first()
  if not existing:
    raise Exception("Cannot update record: existing record not found ({}={})".format(update_key, kwargs[update_key]))  
  existing.set(
    **{ k: v for k, v in kwargs.items() if v != None },
    updated_at = kwargs.get("updated_at", datetime.now())
  )
  commit()
  return existing


def upsert(conn, model, **kwargs):
  """Will create a new row of the given model_ with the properties given by kwargs_.
  If it fails because of uniqueness constraints, the existing row will be updated and returned instead.
  Commits changes."""
  try:
    return insert(conn, model, **kwargs)
  except Exception as e:
    return update(conn, model, update_key=_parse_integrity_error(model, e), **kwargs)


def delete(conn, model, **kwargs):
  """Deletes all rows that match kwargs"""
  query = select(x for x in model)
  for key, val in kwargs.items():
    query.where(lambda x: getattr(x, key) == val)
  query.delete(bulk=True)


def _parse_integrity_error(model, e):
  """Accepts an arbitrary error E, and determines whether it's a PonyORM integrity validation exception that we can recover from.
  If so, this returns the key (i.e. column name) that resulted in the integrity error. If not, the error is re-raised.
  
  This logic is based on errors experienced in practice, and may not represent all possible errors that could arise from integrity checks."""
  if isinstance(e, CacheIndexError):
    regex = r"for key (\w+) already exists|instance with primary key .*? already exists"
  elif isinstance(e, TransactionIntegrityError):
    regex = r"constraint failed: \w+\.(\w+)"
  else:
    raise e
  m = re.search(regex, str(e))
  if not m:
    raise e
  return m.group(1) or 'id'