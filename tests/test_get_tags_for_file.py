import os.path

import tag

from .util import *


def test_get_filetag_should_return_filetags(tmpfile, sample_filetag):
    filetags = list(tag.get_tags_for_file(tmpfile))
    assert filetags[0]["name"] == "testtag"


def test_get_filetag_should_return_empty_cursor_for_missing_file(sample_filetag):
    filetags = list(tag.get_tags_for_file("foo.txt", "testtag"))
    assert len(filetags) == 0
