import pytest
import os.path

import tag


def touch(filename, content="test-content"):
    with open(filename, "w") as f:
        f.write(content)
    return filename


@pytest.fixture
def tmpdb(tmpdir):
    filename = os.path.join(tmpdir, "testdb.sqlite")
    tag.connect(filename, auto_migrate=True)
    return filename


@pytest.fixture
def tmpfile(tmpdir):
    yield touch(os.path.join(tmpdir, "test-filename.txt"))


@pytest.fixture
def tmpfiles(tmpdir):
    # TODO - yield some more interesting files
    yield [
        touch(os.path.join(tmpdir, x))
        for x in ["test-file1", "test-file2", "test-file3"]
    ]


@pytest.fixture
def sample_filetag(tmpdb, tmpfile):
    yield tag.add_filetags(tmpfile, {"testtag": "testvalue"})

@pytest.fixture
def sample_file(tmpdb, tmpfile):
    yield tag.add_file(tmpfile)