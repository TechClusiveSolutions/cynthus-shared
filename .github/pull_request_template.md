## GitHub issue

Closes #XXX

<!-- Use "Closes" so the issue closes automatically on merge. If this PR only partly addresses an issue,
reference it without "Closes" and leave the issue open. -->

## What changed

<!-- One or two sentences. What does this PR do? The diff shows how. -->

## Why

<!-- Link the design document or decision this implements. Skip only for trivial changes. -->

## Verification

<!-- How you know this works: test output, coverage, a live check. -->

- [ ] One class per module, with a matching unit test module
- [ ] `ruff check .` passes
- [ ] `python -m pytest --cov=src --cov-branch --cov-report=json` and `python .github/scripts/check_coverage.py` passes
- [ ] Documentation updated and `markdownlint` passes where behaviour changed

## Deviations from standards

<!-- Anything that knowingly departs from docs/engineering-standards.md, and why. Otherwise write "None". -->

## Scope check

<!-- Confirm the PR does one thing. Unrelated clean-ups belong in their own issue. -->
