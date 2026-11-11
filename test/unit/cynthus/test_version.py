"""The version the system reports is the release in the change log"""

import re
from pathlib import Path

import cynthus

CHANGELOG = Path(__file__).resolve().parents[3] / 'CHANGELOG.md'


def test_the_reported_version_is_the_latest_dated_release_in_the_change_log():
    releases = re.findall(r'^## \[(\d+\.\d+\.\d+)\] - \d{4}-\d{2}-\d{2}$', CHANGELOG.read_text(encoding='utf-8'), re.M)

    # A release renames Unreleased to the version and date, and changes __VERSION__ in the same pull request
    assert cynthus.__VERSION__ == releases[0]
