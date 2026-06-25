import argparse
import os
import sys
import textwrap
from . import data
from . import base
import subprocess


def main():
    args = parse_args()
    args.func(args)


def parse_args():
    parser = argparse.ArgumentParser(description="ugit: a simple git implementation")

    command = parser.add_subparsers(dest="command", required=True)

    oid = base.get_oid

    init_parser = command.add_parser("init", help="Initialize a new ugit repository")
    init_parser.set_defaults(func=init)

    hash_object_parser = command.add_parser(
        "hash-object", help="Compute object ID and optionally create a blob from a file"
    )
    hash_object_parser.set_defaults(func=hash_object)
    hash_object_parser.add_argument("file", help="File to hash")

    cat_file_parser = command.add_parser("cat-file", help="retrieval of blob")
    cat_file_parser.set_defaults(func=cat_file)
    cat_file_parser.add_argument("object", type=oid)

    write_tree_parser = command.add_parser(
        "write-tree", help="Create a tree object from the current index"
    )
    write_tree_parser.set_defaults(func=write_tree)

    read_tree_parser = command.add_parser(
        "read-tree",
        help="Retrieve an OID of a tree and extract it to the working directory",
    )
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument("tree", type=oid)

    commit_parser = command.add_parser(
        "commit", help="Record changes to the repository"
    )
    commit_parser.set_defaults(func=commit)
    commit_parser.add_argument("-m", "--message", required=True)

    log_parser = command.add_parser("log", help="Show commit logs")
    log_parser.set_defaults(func=log)
    log_parser.add_argument("oid", type=oid, default="@", nargs="?")

    checkout_parser = command.add_parser("checkout", help="Checkout a commit")
    checkout_parser.set_defaults(func=checkout)
    checkout_parser.add_argument("commit")

    tag_parser = command.add_parser("tag", help="Create a tag")
    tag_parser.set_defaults(func=tag)
    tag_parser.add_argument("name", help="Name of the tag")
    tag_parser.add_argument("oid", type=oid, default="@", nargs="?")
    
    branch_parser = command.add_parser("branch", help="Create a branch")
    branch_parser.set_defaults(func=branch)
    branch_parser.add_argument('name',nargs="?", help="Name of the branch")
    branch_parser.add_argument('start_point', default='@',type=oid,nargs='?')
    
    status_parser = command.add_parser('status', help='Show the working directory status')
    status_parser.set_defaults(func=status)
    
    k_parser = command.add_parser("k", help="show the commit history as a graph")
    k_parser.set_defaults(func=k)

    return parser.parse_args()


def init(args):
    base.init()
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


def log(args):
    for oid in base.iter_commits_and_parents({args.oid}):
        commit = base.get_commit(oid)

        print(f"commit {oid}\n")
        print(textwrap.indent(commit.message, "    "))
        print("")


def checkout(args):
    base.checkout(args.commit)


def tag(args):
    base.create_tag(args.name, args.oid)


def k(args):
    dot = "digraph commits {\n"
    oids = set()
    for refname, ref in data.iter_refs(deref=False):
        dot += f'"{refname}" [shape=note]\n'
        dot += f'"{refname}" -> "{ref.value}"\n\n'
        if not ref.symbolic:
            oids.add(ref.value)

    for oid in base.iter_commits_and_parents(oids):
        commit = base.get_commit(oid)
        dot += f'"{oid}" [shape=box style=filled label="{oid[:10]}"]\n'
        if commit.parent:
            dot += f'"{oid}" -> "{commit.parent}"\n'
        dot+='\n'
        
    dot += "}"
    print(dot)

    with subprocess.Popen(
        ['dot',  "-Tsvg", "-o", "graph.svg"], stdin=subprocess.PIPE
    ) as proc:
        proc.communicate(dot.encode())
        
def branch(args):
    base.create_branch(args.name,args.start_point)
    print (f'Branch {args.name} created at {args.start_point[:10]}')

def status(args):
    HEAD = base.get_oid('@')
    branch = base.get_branch_name()
    if branch:
        print(f'On branch {branch}')
    else:
        print(f'HEAD detached at {HEAD[:10]}')

if __name__ == "__main__":
    main()
