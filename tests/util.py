import pytest
import os.path

import tag


def touch(filename, content="test-content"):
    with open(filename, "w") as f:
        f.write(content)
    return filename

@pytest.fixture
def conn(tmpdir):
    with tag.connect(os.path.join(tmpdir, "testdb.sqlite")) as c:
        yield c


@pytest.fixture
def tmpfile(tmpdir):
    yield touch(os.path.join(tmpdir, "test-filename"))

@pytest.fixture
def tmpfiles(tmpdir):
    # TODO - yield some more interesting files
    yield [touch(os.path.join(tmpdir, x)) for x in ['test-file1', 'test-file2', 'test-file3']]


@pytest.fixture
def sample_file_tag(conn, tmpfile):
    yield tag.add_file_tags(conn, tmpfile, {"testtag": "testvalue"})