import os.path

import tag

from .util import *


def test_add_file_should_create_new_file(tmpdb, tmpfile):
    tag.add_file(tmpfile)
    assert tag.count_files() == 1


def test_add_file_should_update_existing_file(tmpdb, tmpfile):
    tag.add_file(tmpfile)
    tag.add_file(tmpfile)
    assert tag.count_files() == 1


def test_add_file_should_not_update_existing_file_if_filename_different(tmpdb, tmpfiles):
    [tag.add_file(x) for x in tmpfiles]
    assert tag.count_files() == len(tmpfiles)


def test_add_file_should_escape_uri_values(tmpdb, tmpdir):
    filename = touch(os.path.join(tmpdir, "test\\file name"))
    tag.add_file(filename)
    assert "test%5Cfile%20name" in tag.get_file(filename)["uri"]