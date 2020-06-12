import os.path
import pony.orm as orm

import tag

from .util import *

def test_get_file_should_return_file(conn, tmpfile, sample_filetag):
  file = tag.get_file(conn, tmpfile)
  assert file.name == "test-filename"

def test_get_file_should_return_None_for_missing_files(conn, tmpfile, sample_filetag):
  file = tag.get_file(conn, "foo.txt")
  assert file is None
