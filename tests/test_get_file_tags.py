import os.path
import pony.orm as orm

import tag

from .util import *

def test_get_filetags_should_return_filetags(conn, tmpfile, sample_filetag):
  filetags = tag.get_filetags(conn, tmpfile)
  assert filetags.first().tag.name == "testtag"

def test_get_filetags_should_return_empty_cursor_for_missing_file(conn, tmpfile, sample_filetag):
  filetags = tag.get_filetags(conn, "foo.txt")
  assert len(filetags) == 0