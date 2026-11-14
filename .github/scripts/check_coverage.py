#!/usr/bin/env python3
"""Fail when line or branch coverage is below its target.

pytest-cov can gate only one combined number, so this reads the JSON report (`--cov-report=json`, with `--cov-branch`)
and checks lines and branches separately, as the Cynthus engineering standards ask.

Usage: python3 .github/scripts/check_coverage.py [coverage.json] [--lines 90] [--branches 80]
"""

import argparse
import json
import sys


def measure(report: dict) -> tuple[float, float | None, str]:
    """Return (line percent, branch percent or None when there are no branches, text) from a coverage.py JSON report."""

    totals = report['totals']

    if 'covered_branches' not in totals:
        raise ValueError('the report has no branch data; run pytest with --cov-branch')

    statements = totals['num_statements']
    lines = 100.0 if statements == 0 else 100.0 * totals['covered_lines'] / statements
    branches = None if totals['num_branches'] == 0 else 100.0 * totals['covered_branches'] / totals['num_branches']
    text = (f"lines {lines:.2f}% ({totals['covered_lines']}/{statements}), "
            + ('branches none' if branches is None else
               f"branches {branches:.2f}% ({totals['covered_branches']}/{totals['num_branches']})"))

    return lines, branches, text


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('report', nargs='?', default='coverage.json')
    parser.add_argument('--lines', type=float, default=90.0)
    parser.add_argument('--branches', type=float, default=80.0)
    args = parser.parse_args(argv)

    try:
        with open(args.report, encoding='utf-8') as handle:
            lines, branches, text = measure(json.load(handle))
    except (OSError, ValueError, KeyError) as error:
        print(f'{args.report}: {error}')

        return 2

    print(f'{args.report}: {text}; targets lines {args.lines:g}%, branches {args.branches:g}%')
    problems = []

    if lines < args.lines:
        problems.append(f'line coverage {lines:.2f}% is below {args.lines:g}%')

    if branches is not None and branches < args.branches:
        problems.append(f'branch coverage {branches:.2f}% is below {args.branches:g}%')

    for problem in problems:
        print(f'FAIL: {problem}')

    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
