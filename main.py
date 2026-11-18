#!/usr/bin/env python3
"""Ship the finished 18 Nov 2026 news page as the competition entry.

The artwork itself (entry.png) is pre-rendered by the PIL composer in
the same directory; this entrypoint only places a copy of it where the
harness expects the deliverable, at /output/entry.png.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
TARGET_DIR = "/output"
TARGET = os.path.join(TARGET_DIR, "entry.png")


def main():
    os.makedirs(TARGET_DIR, exist_ok=True)
    shutil.copyfile(SOURCE, TARGET)
    size = os.path.getsize(TARGET)
    print("wrote %s (%d bytes)" % (TARGET, size))


if __name__ == "__main__":
    main()
