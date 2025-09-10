import argparse
import os
import sys
from . import data
from . import base


def main():
    args = parse_args()
    args.func(args)


def parse_args():
    parser = argparse.ArgumentParser(description="ugit: a simple git implementation")

    command = parser.add_subparsers(dest="command", required=True)

    init_parser = command.add_parser("init", help="Initialize a new ugit repository")
    init_parser.set_defaults(func=init)

    hash_object_parser = command.add_parser(
        "hash-object", help="Compute object ID and optionally create a blob from a file"
    )
    hash_object_parser.set_defaults(func=hash_object)
    hash_object_parser.add_argument("file", help="File to hash")

    cat_file_parser = command.add_parser("cat-file", help="retrieval of blob")
    cat_file_parser.set_defaults(func=cat_file)
    cat_file_parser.add_argument("object")

    write_tree_parser = command.add_parser(
        "write-tree", help="Create a tree object from the current index"
    )
    write_tree_parser.set_defaults(func=write_tree)

    read_tree_parser = command.add_parser(
        "read-tree",
        help="Retrieve an OID of a tree and extract it to the working directory",
    )
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument("tree")

    commit_parser = command.add_parser(
        "commit", help="Record changes to the repository"
    )
    commit_parser.set_defaults(func=commit)
    commit_parser.add_argument("-m", "--message", required=True)

    return parser.parse_args()


def init(args):
    data.init()
    print(
        f"Initialized empty ugit repository in {os.path.join(os.getcwd(),data.GIT_DIR)}"
    )


def hash_object(args):
    with open(args.file, "rb") as f:
        print(data.hash_object(f.read()))


def cat_file(args):
    sys.stdout.flush()
    sys.stdout.buffer.write(data.get_object(args.object, expected=None))


def write_tree(args):
    print(base.write_tree())


def read_tree(args):
    base.read_tree(args.tree)


def commit(args):
    print(base.commit(args.message))


if __name__ == "__main__":
    main()
