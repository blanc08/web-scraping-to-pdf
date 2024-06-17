from os import path
import os
from constant import CATEGORIES


def make_output_dir():
    """
    prepare output directories
    """
    base_dir = ("out/pdf", "out/html", "out/csv")

    for base in base_dir:
        for row in CATEGORIES:
            os.makedirs(path.join(path.curdir, base, row), exist_ok=True)
