import os
import hashlib

GIT_DIR = ".ugit"


def init():
    os.makedirs(GIT_DIR, exist_ok=True)
    os.makedirs(f"{GIT_DIR}/objects", exist_ok=True)


def hash_object(data):
    oid = hashlib.sha1(data).hexdigest()
    with open(f"{GIT_DIR}/objects/{oid}", "wb") as out:
        out.write(data)
    return oid


# The hash_object function computes the SHA-1 hash of the input data, stores it in the .ugit/objects directory, and returns the hash.
