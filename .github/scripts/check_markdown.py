"""Check the Markdown files of a repository for things a screen reader (or a plain terminal) trips over.

The rules, each reported with file and line:

* ASCII only (no dashes, arrows, box-drawing characters, emoji or other symbols);
* no pipe tables (write a list: one item per row, with the columns as nested items);
* Unix line endings, no trailing spaces (two spaces for a line break are allowed) and a final newline;
* every fenced code block names its language (use ``text`` for plain output);
* the file is named ``README.md``, not ``READMe.md`` or ``readme.md``;
* relative links point at a file that exists, and a ``#fragment`` points at a heading that exists.

Run it from the repository root: ``python3 .github/scripts/check_markdown.py``. It exits 1 when anything is reported.
"""

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

FENCE = re.compile(r'^\s*(```+|~~~+)(.*)$')
ROW = re.compile(r'^\s*\|.*\|\s*$')
SEPARATOR = re.compile(r'^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$')
HEADING = re.compile(r'^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$')
LINK = re.compile(r'(?<!!)\[(?:[^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
SCHEME = re.compile(r'^[a-zA-Z][a-zA-Z0-9+.-]*:')


def tracked(root: Path) -> list[Path]:
    try:
        names = subprocess.check_output(['git', 'ls-files', '*.md'], cwd=root, text=True).split('\n')
    except (OSError, subprocess.CalledProcessError):
        names = [str(p.relative_to(root)) for p in root.rglob('*.md') if '.git' not in p.parts]

    return [root / n for n in names if n]


def slug(text: str) -> str:
    text = re.sub(r'`([^`]*)`', r'\1', text)
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'[*_~]', '', text).strip().lower()
    text = re.sub(r'[^\w\- ]', '', text)

    return text.replace(' ', '-')


def headings(path: Path) -> set[str]:
    found: dict[str, int] = {}
    anchors: set[str] = set()
    fence = False

    for line in path.read_text(encoding='utf-8', errors='replace').split('\n'):
        if FENCE.match(line):
            fence = not fence
        match = None if fence else HEADING.match(line)

        if match:
            base = slug(match.group(2))
            count = found.get(base, 0)
            found[base] = count + 1
            anchors.add(base if count == 0 else f'{base}-{count}')

    return anchors


def check(path: Path, root: Path) -> list[str]:
    problems: list[str] = []
    name = path.relative_to(root).as_posix()
    raw = path.read_bytes()

    if path.name.lower() == 'readme.md' and path.name != 'README.md':
        problems.append(f'{name}: name the file README.md')

    if b'\r' in raw:
        problems.append(f'{name}: has CR line endings (use LF)')

    if raw and not raw.endswith(b'\n'):
        problems.append(f'{name}: no newline at the end of the file')

    lines = raw.decode('utf-8', errors='replace').split('\n')
    fence = False
    anchors: dict[Path, set[str]] = {}

    for number, line in enumerate(lines, 1):
        line = line.rstrip('\r')
        bad = sorted({c for c in line if ord(c) > 127})

        if bad:
            problems.append(f'{name}:{number}: non-ASCII character {", ".join(f"U+{ord(c):04X}" for c in bad)}')

        opened = FENCE.match(line)

        if opened:
            if not fence and not opened.group(2).strip():
                problems.append(f'{name}:{number}: code block without a language (use text)')

            fence = not fence
            continue

        if fence:
            continue

        trailing = len(line) - len(line.rstrip(' '))

        if trailing and trailing != 2:
            problems.append(f'{name}:{number}: trailing spaces')

        if ROW.match(line) and number < len(lines) and SEPARATOR.match(lines[number]) and '-' in lines[number]:
            problems.append(f'{name}:{number}: pipe table (write a list instead)')

        for target in LINK.findall(re.sub(r'`[^`]*`', '', line)):
            if SCHEME.match(target) or target.startswith(('mailto:', '//')):
                continue

            file_part, _, fragment = target.partition('#')
            file_part = unquote(file_part)
            where = (path.parent / file_part) if file_part else path

            if file_part and not where.exists():
                problems.append(f'{name}:{number}: link to {target} - no such file')
            elif fragment and where.suffix == '.md' and where.exists():
                known = anchors.setdefault(where, headings(where))

                if unquote(fragment).lower() not in known:
                    problems.append(f'{name}:{number}: link to {target} - no such heading')

    return problems


def main() -> int:
    root = Path.cwd()
    problems = [p for path in tracked(root) for p in check(path, root)]

    for problem in problems:
        print(problem)

    print(f'{len(problems)} problem(s)')

    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
