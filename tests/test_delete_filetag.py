import os.path
import pony.orm as orm

import tag

from .util import *

def test_delete_filetag_should_delete_filetags_from_db(tmpdb, tmpfile, sample_filetag):
    assert tag.count_filetags() == 1
    tag.delete_filetag(tmpfile, "testtag")
    assert tag.count_filetags() == 0

def test_delete_filetag_shouldnt_delete_files_from_db(tmpdb, tmpfile, sample_filetag):
    tag.delete_filetag(tmpfile, "testtag")
    assert tag.count_files() == 1

def test_delete_filetag_shouldnt_delete_tags_from_db(tmpdb, tmpfile, sample_filetag):
    tag.delete_filetag(tmpfile, "testtag")
    assert tag.count_tags() == 1

def test_delete_filetags_should_ignore_filetags_not_in_db(tmpdb, tmpfile, sample_filetag):
    tag.delete_filetag(tmpfile, "testwrongtag")
    assert tag.count_filetags() == 1
