import os.path
import pony.orm as orm

import tag

from .util import *

def test_get_tag_should_return_tag(conn, tmpfile, sample_file_tag):
  t = tag.get_tag(conn, "testtag")
  assert t.name == "testtag"

def test_get_tag_should_return_None_for_missing_tags(conn, tmpfile, sample_file_tag):
  t = tag.get_tag(conn, "wrongtag")
  assert t is None
