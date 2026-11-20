#!/usr/bin/env python3
"""Copy the pre-rendered front page to the output directory.

The image (entry.png, rendered by render.py on the build machine) is
committed to this repo; this program only copies it, stdlib only.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(os.path.join(HERE, "entry.png"),
                    os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
