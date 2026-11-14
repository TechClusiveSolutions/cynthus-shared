#!/usr/bin/env python3
"""Fail when a tracked text file is committed with CRLF or mixed line endings.

Cynthus keeps Unix line endings (LF) in every text file. Files that Windows needs with CRLF (.bat, .cmd) are pinned by
`.gitattributes` with `eol=crlf` and are skipped. Run from the repository root: `python3 .github/scripts/check_line_endings.py`.
"""

import subprocess
import sys


def offenders() -> list[tuple[str, str]]:
    """The tracked text files whose committed content is CRLF or mixed, as (state, path) pairs."""

    out = subprocess.run(['git', 'ls-files', '--eol'], capture_output=True, text=True, check=True).stdout
    found = []

    for line in out.splitlines():
        meta, _, path = line.partition('\t')
        parts = meta.split()

        if len(parts) < 3:
            continue

        index, attr = parts[0], ' '.join(parts[2:])

        if index in ('i/crlf', 'i/mixed') and 'eol=crlf' not in attr:
            found.append((index[2:], path))

    return found


def main() -> int:
    bad = offenders()

    for state, path in bad:
        print(f'{path}: {state} line endings; use LF (run `dos2unix {path}` or `git add --renormalize .`)')

    print(f'{len(bad)} problem(s)')

    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
