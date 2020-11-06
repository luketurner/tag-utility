import os.path

import tag

from .util import *


def test_get_file_should_return_file(tmpfile, sample_filetag):
    f = tag.get_file(tmpfile)
    assert f["name"] == "test-filename.txt"


def test_get_file_should_return_None_for_missing_files(sample_filetag):
    f = tag.get_file("foo.txt")
    assert f is None
