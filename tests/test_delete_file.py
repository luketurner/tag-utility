import os.path

import tag

from .util import *


def test_delete_file_should_delete_file_from_db(tmpdb, tmpfile, sample_filetag):
    assert tag.count_files() == 1
    tag.delete_file(tmpfile)
    assert tag.count_files() == 0


# TODO -- fix me
# def test_delete_file_should_delete_filetags_from_db(tmpdb, tmpfile, sample_filetag):
#     assert tag.count_filetags() == 1
#     tag.delete_file(tmpfile)
#     assert tag.count_filetags() == 0


def test_delete_file_shouldnt_delete_tags_from_db(tmpdb, tmpfile, sample_filetag):
    tag.delete_file(tmpfile)
    assert tag.count_tags() == 1


def test_delete_file_should_do_nothing_if_file_doesnt_exist_in_db(
    tmpdb, tmpfile, sample_filetag
):
    tag.delete_file("foo.txt")
    assert tag.count_files() == 1
