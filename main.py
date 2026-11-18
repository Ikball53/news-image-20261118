#!/usr/bin/env python3
"""news-image-20261118 v1 entry runner.

Copies the finished front-page artwork (entry.png, bundled next to this
script) into the grading output directory. Pure standard library, no
network, no randomness, no timestamps: the bytes written are identical
on every run.
"""

import hashlib
import os
import shutil
import sys

# Artwork shipped with this entry and the required output location.
SOURCE_NAME = "entry.png"
OUTPUT_DIR = "/output"
OUTPUT_NAME = "entry.png"


def locate_source() -> str:
    """Return the path of the bundled artwork next to this script."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(here, SOURCE_NAME)
    if not os.path.isfile(candidate):
        raise FileNotFoundError("bundled artwork not found: " + candidate)
    return candidate


def file_digest(path: str) -> str:
    """SHA-256 of a file, read in fixed-size chunks."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def publish(source: str) -> str:
    """Copy the artwork to /output/entry.png and return its digest."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    target = os.path.join(OUTPUT_DIR, OUTPUT_NAME)
    shutil.copyfile(source, target)
    # Guard against a truncated copy: byte counts must agree exactly.
    if os.path.getsize(target) != os.path.getsize(source):
        raise IOError("copy size mismatch for " + target)
    return file_digest(target)


def main() -> int:
    source = locate_source()
    before = file_digest(source)
    after = publish(source)
    if before != after:
        print("mismatch: output digest differs from source", file=sys.stderr)
        return 1
    print("wrote " + os.path.join(OUTPUT_DIR, OUTPUT_NAME) + " sha256=" + after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
