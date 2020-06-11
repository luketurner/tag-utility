import os.path
import pony.orm as orm

import tag

from .util import *

def test_search_with_no_arguments_should_return_all_files(conn, tmpfile, sample_file_tag):
  files = tag.search(conn)
  assert len(files) == 1

def test_search_with_no_tags_should_return_matching_files(conn, tmpfile, sample_file_tag):
  assert len(tag.search(conn, tags={"testtag": None})) == 1
  assert len(tag.search(conn, tags={"badtag": None})) == 0