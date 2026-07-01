"""
project.py — CS50P Final Project entry point for ugit.

ugit is a small, from-scratch reimplementation of Git's core internals
(object storage, refs, trees, commits, branching, merging) built as a
real Python package under ugit/. This file is the top-level entry point
required by CS50P: it exposes main() plus several standalone, testable
functions that drive the package.

Run it directly to try a guided demo of the core workflow:
    python project.py
"""

import os
from ugit import data, base


def init_repo(path="."):
    """
    Initializes a new ugit repository inside the given path.
    Returns True on success. Raises FileExistsError if a repository
    already exists at that path, so callers can't silently clobber one.
    """
    with data.change_git_dir(path):
        if os.path.isdir(data.GIT_DIR):
            raise FileExistsError(f"A ugit repository already exists at {path}")
        base.init()
    return True


def hash_file(filepath):
    """
    Hashes the contents of filepath and stores it as a blob object.
    Returns the resulting 40-character SHA-1 object id.
    Raises FileNotFoundError with a clear message if the file doesn't exist.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"No such file: {filepath}")
    with open(filepath, "rb") as f:
        return data.hash_object(f.read())


def stage_files(filenames):
    """
    Stages the given list of files (and/or directories) into the index
    by delegating to base.add(). Returns the number of top-level paths
    that were processed.
    """
    base.add(filenames)
    return len(filenames)


def make_commit(message):
    """
    Commits whatever is currently staged in the index, using the given
    commit message. Returns the new commit's object id. Raises ValueError
    if the message is empty, since an empty commit message isn't useful.
    """
    if not message or not message.strip():
        raise ValueError("Commit message cannot be empty")
    return base.commit(message)


def get_log(start="@"):
    """
    Returns a list of human-readable strings describing each commit
    reachable from 'start' (default: the current HEAD), most recent first.
    Each string contains the short object id and the commit message.
    """
    oid = base.get_oid(start)
    lines = []
    for commit_oid in base.iter_commits_and_parents({oid}):
        commit = base.get_commit(commit_oid)
        short_oid = commit_oid[:10]
        first_line = commit.message.splitlines()[0] if commit.message else ""
        lines.append(f"{short_oid}  {first_line}")
    return lines


def main():

    demo_dir = "demo_repo"
    os.makedirs(demo_dir, exist_ok=True)
    os.chdir(demo_dir)

    # GIT_DIR is only set while inside this context (see data.change_git_dir),
    # so the whole demo workflow needs to run inside one shared context here,
    # just like ugit's own CLI does in cli.main().

    with data.change_git_dir("."):
        print(
            f"Initialized empty ugit repository in {os.path.join(os.getcwd(),data.GIT_DIR)}"
        )
        init_repo()

        sample_path = "hello.txt"
        with open(sample_path, "w") as f:
            f.write("Hello, ugit!\n")

        print(f"Hashing and staging {sample_path} ...")
        oid = hash_file(sample_path)
        print(f"  blob oid: {oid}")
        stage_files([sample_path])

        print("Creating a commit ...")
        commit_oid = make_commit("Initial commit from project.py demo")
        print(f"  commit oid: {commit_oid}")

        print("\nCommit history:")
        for line in get_log():
            print(f"  {line}")


if __name__ == "__main__":
    main()
