#!/usr/bin/env python3
"""main.py - entrypoint for make.fun news-image-20261124.

Copies the pre-drawn entry.png (rendered by draw.py, same repository)
to the grader output directory as entry.png.
Python 3.13 standard library only. No network, no environment secrets,
no eval, no dynamic code loading: it only copies a shipped file.
"""
import os
import shutil


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    size = os.path.getsize(dst)
    if size > 1048576:
        raise SystemExit("entry.png exceeds the 1 MiB limit: %d bytes" % size)
    print("wrote %s (%d bytes)" % (dst, size))


if __name__ == "__main__":
    main()
