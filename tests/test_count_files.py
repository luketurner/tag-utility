import os.path

import tag

from .util import *


def test_count_with_no_criteria_should_count_everything(sample_filetag):
    assert tag.count_files() == 1


def test_count_should_include_files_matching_tags(sample_filetag):
    assert tag.count_files(tags=["testtag"]) == 1


def test_count_should_not_include_files_with_partial_tag_matches(sample_filetag):
    assert tag.count_files(tags=["testtag", "othertag"]) == 0


def test_count_should_not_include_files_without_matching_tags(sample_filetag):
    assert tag.count_files(tags=["badtag"]) == 0


def test_count_should_exclude_files_based_on_exclude_tags(sample_filetag):
    assert tag.count_files(exclude_tags=["testtag"]) == 0


def test_count_should_include_files_matching_any_mime_types(sample_filetag):
    assert tag.count_files(mime_types=["text/plain", "foo/bar"]) == 1


def test_count_should_exclude_files_with_exclude_mime_types(sample_filetag):
    assert tag.count_files(exclude_mime_types=["text/plain"]) == 0


def test_count_should_match_files_with_no_tags(sample_file):
    assert tag.count_files() == 1
