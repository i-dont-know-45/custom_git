import argparse

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
    print("Hello, World!")


if __name__ == "__main__":
    main()
    
#created a command 'init' that prints 'Hello, World!' when you write 'ugit init' in the terminal
    
