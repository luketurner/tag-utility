import os.path
import pony.orm as orm

import tag

from .util import *

def test_get_file_tags_should_return_filetags(conn, tmpfile, sample_file_tag):
  filetags = tag.get_file_tags(conn, tmpfile)
  assert filetags.first().tag.name == "testtag"

def test_get_file_tags_should_return_empty_cursor_for_missing_file(conn, tmpfile, sample_file_tag):
  filetags = tag.get_file_tags(conn, "foo.txt")
  assert len(filetags) == 0