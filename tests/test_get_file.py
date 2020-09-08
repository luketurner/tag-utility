import os.path
import pony.orm as orm

import tag

from .util import *


def test_get_file_should_return_file(tmpdb, tmpfile, sample_filetag):
    f = tag.get_file(tmpfile)
    assert f["name"] == "test-filename"


def test_get_file_should_return_None_for_missing_files(tmpdb, tmpfile, sample_filetag):
    f = tag.get_file("foo.txt")
    assert f is None
