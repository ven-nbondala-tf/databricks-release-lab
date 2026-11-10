#!/usr/bin/env python3
"""Fail if an instruction file is over the Genie Code limit of 20,000 characters.

Usage:
    python scripts/check_length.py [folder]

The folder defaults to the instructions folder next to this script.
Genie Code ignores anything past the limit, so a file that is too long
would be deployed with its last rules silently dropped.
"""
import sys
from pathlib import Path

LIMIT = 20_000


def main(argv):
    if len(argv) > 1:
        folder = Path(argv[1])
    else:
        folder = Path(__file__).resolve().parent.parent / "instructions"

    files = sorted(folder.glob("*.md"))
    if not files:
        print(f"No .md files found in {folder}")
        return 1

    failed = False
    for path in files:
        size = len(path.read_text(encoding="utf-8"))
        ok = size <= LIMIT
        print(f"{path.name}: {size} of {LIMIT} characters, {'ok' if ok else 'TOO LONG'}")
        if not ok:
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
