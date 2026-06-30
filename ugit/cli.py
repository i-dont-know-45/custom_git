import argparse
import os
import sys
import textwrap
from . import data
from . import base
from . import diff
from . import remote
import subprocess


def main():
    with data.change_git_dir("."):
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
    
    show_parser =command.add_parser('show', help='Show a commit')
    show_parser.set_defaults(func=show)
    show_parser.add_argument('oid', type=oid,default='@', nargs='?')
    
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
    
    reset_parser = command.add_parser('reset', help='Reset the working directory')
    reset_parser.set_defaults(func=reset)
    reset_parser.add_argument('commit', type=oid,)
    
    diff_parser = command.add_parser('diff', help='Show the changes between commits')
    diff_parser.set_defaults(func=_diff)
    diff_parser.add_argument('commit',type=oid,default='@',nargs='?')
    
    k_parser = command.add_parser("k", help="show the commit history as a graph")
    k_parser.set_defaults(func=k)
    
    merge_parser = command.add_parser('merge', help='merge two branches')
    merge_parser.set_defaults(func=merge)
    merge_parser.add_argument('commit',type=oid)
    
    merge_base_parser = command.add_parser("merge-base", help="Find merge base")
    merge_base_parser.set_defaults(func=merge_base)
    merge_base_parser.add_argument('commit1',type=oid)
    merge_base_parser.add_argument('commit2',type=oid)
    
    fetch_parser = command.add_parser('fetch', help='Fetch from a remote repository')
    fetch_parser.set_defaults(func=fetch)
    fetch_parser.add_argument('remote')
    
    push_parser = command.add_parser('push', help='Push to a remote repository')
    push_parser.set_defaults(func=push)
    push_parser.add_argument('remote')
    push_parser.add_argument('branch')
    
    add_parser = command.add_parser('add', help='Add files to the index')
    add_parser.set_defaults(func=add)
    add_parser.add_argument('files',nargs="+")
    
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

def _print_commit(oid,commit,refs=None):
    refs_str = f' ({", ".join(refs)})' if refs else ""
    print(f"commit {oid}{refs_str}\n")
    print(textwrap.indent(commit.message, "    "))
    print("")

def log(args):
    refs={}
    for refname,ref in data.iter_refs():
        refs.setdefault(ref.value, []).append(refname)
        
    for oid in base.iter_commits_and_parents({args.oid}):
        commit = base.get_commit(oid)
        _print_commit(oid,commit,refs.get(oid))

def show(args):
    if not args.oid:
        return
    commit = base.get_commit(args.oid)
    parent_tree = None
    if commit.parents:
        parent_tree = base.get_commit(commit.parents[0]).tree
    _print_commit(args.oid,commit)
    result = diff.diff_trees(base.get_tree(parent_tree),base.get_tree(commit.tree))
    sys.stdout.flush()
    sys.stdout.buffer.write(result)
    

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
        for parent in commit.parents:
            dot += f'"{oid}" -> "{parent}"\n'   
        dot+='\n'
        
    dot += "}"
    print(dot)

    with subprocess.Popen(
        ['dot',  "-Tsvg", "-o", "graph.svg"], stdin=subprocess.PIPE
    ) as proc:
        proc.communicate(dot.encode())
        
def branch(args):
    if not args.name:
        current = base.get_branch_name()
        for branch in base.iter_branch_names():
            prefix = '*' if branch==current else ' '
            print(f'{prefix}{branch}')
    else:
        base.create_branch(args.name,args.start_point)
        print (f'Branch {args.name} created at {args.start_point[:10]}')

def status(args):
    HEAD = base.get_oid('@')
    branch = base.get_branch_name()
    if branch:
        print(f'On branch {branch}')
    else:
        print(f'HEAD detached at {HEAD[:10]}')
       
    MERGE_HEAD = data.get_ref('MERGE_HEAD').value
    if MERGE_HEAD:
        print(f'Merging with {MERGE_HEAD[:10]}')
    print('\nChanges to be commited\n')
    HEAD_tree = HEAD and base.get_commit(HEAD).tree
    for path , action in diff.iter_changed_files(base.get_tree(HEAD_tree),base.get_working_tree()):
        print(f'{action:>12}: {path}')
        

def reset(args):
    base.reset(args.commit)
    
def _diff(args):
    tree = args.commit and base.get_commit(args.commit).tree
    
    result = diff.diff_trees(base.get_tree(tree),base.get_working_tree())
    sys.stdout.flush()
    sys.stdout.buffer.write(result)
    
def merge(args):
    base.merge(args.commit)

def merge_base(args):
    print(base.get_merge_base(args.commit1,args.commit2))

def fetch(args):
    remote.fetch(args.remote)

def push(args):
    remote.push(args.remote,f'refs/heads/{args.branch}')

def add(args):
    base.add(args.files)

if __name__ == "__main__":
    main()