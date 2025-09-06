import argparse
import os
import sys
from . import data


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
    sys.stdout.buffer.write(data.get_object(args.object,expected=None))


if __name__ == "__main__":
    main()

