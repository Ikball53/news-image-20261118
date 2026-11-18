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

# Post-copy integrity check: the copied entry must be byte-identical to the source.
import hashlib as _hashlib, os as _os
_src = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "entry.png")
_dst = "/output/entry.png"
def _sha256(p):
    _h = _hashlib.sha256()
    with open(p, "rb") as _f:
        for _chunk in iter(lambda: _f.read(65536), b""):
            _h.update(_chunk)
    return _h.hexdigest()
# The judge copies /output itself; a mismatch means the entry on disk is not the
# image that was reviewed, so fail loudly instead of submitting a stale copy.
if _os.path.exists(_dst) and _sha256(_src) != _sha256(_dst):
    raise SystemExit("entry.png copy mismatch: %s != %s" % (_src, _dst))
