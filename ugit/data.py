import os

GIT_DIR = ".ugit"


def init():
    os.makedirs(GIT_DIR, exist_ok=True)


# This function creates a directory named .ugit in the current working directory if it doesn't already exist
