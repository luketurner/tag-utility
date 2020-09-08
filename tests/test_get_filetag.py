import os.path
import pony.orm as orm

import tag

from .util import *

def test_get_filetag_should_return_filetags(tmpdb, tmpfile, sample_filetag):
  filetag = tag.get_filetag(tmpfile, "testtag")
  assert filetag["name"] == "testtag"

def test_get_filetag_should_return_empty_cursor_for_missing_file(tmpdb, tmpfile, sample_filetag):
  filetag = tag.get_filetag("foo.txt", "testtag")
  assert filetag == None