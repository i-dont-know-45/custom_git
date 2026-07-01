"""
test_project.py — pytest tests for project.py

Each test runs inside a pytest-provided temporary directory (tmp_path)
so they never touch real files, and monkeypatch is used to chdir into
that temp directory for the duration of each test.
"""

import pytest
from project import init_repo, hash_file, stage_files, make_commit, get_log


def test_init_repo(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = init_repo()
    assert result is True
    assert (tmp_path / ".ugit").is_dir()
    assert (tmp_path / ".ugit" / "objects").is_dir()

    # initializing a second time on top of an existing repo should fail loudly
    with pytest.raises(FileExistsError):
        init_repo()


def test_hash_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_repo()
    
    sample = tmp_path / "sample.txt"
    sample.write_text("Hello world")

    oid = hash_file(sample)
    assert len(oid) == 40
    assert all(c in "0123456789abcdef" for c in oid)

    # hashing identical content twice must give the same oid (content-addressing)
    oid_again = hash_file(sample)
    assert oid == oid_again

    with pytest.raises(FileNotFoundError):
        hash_file("does_not_exist.txt")


def test_make_commit(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_repo()

    sample = tmp_path / "sample.txt"
    sample.write_text("Hello world")
    stage_files([sample])

    commit = make_commit("first commit")
    assert len(commit) == 40

    with pytest.raises(ValueError):
        make_commit(" ")


def test_get_log(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_repo()

    sample = tmp_path / "sample.txt"
    sample.write_text("Hello world")
    stage_files([sample])
    make_commit("first commit")

    sample.write_text("version two")
    stage_files(["sample.txt"])
    make_commit("second commit")

    log_lines = get_log()
    assert len(log_lines) == 2
    assert "second commit" in log_lines[0]
    assert "first commit" in log_lines[1]
 