import argparse
import os
from . import data


def main():
    args = parse_args()
    args.func(args)


def parse_args():
    parser = argparse.ArgumentParser(description="ugit: a simple git implementation")

    command = parser.add_subparsers(dest="command", required=True)

    init_parser = command.add_parser("init", help="Initialize a new ugit repository")
    init_parser.set_defaults(func=init)

    return parser.parse_args()


def init(args):
    data.init()
    print(
        f"Initialized empty ugit repository in {os.path.join(os.getcwd(),data.GIT_DIR)}"
    )


if __name__ == "__main__":
    main()


# We initiate the repository by creating a .ugit directory using the init function from data.py
