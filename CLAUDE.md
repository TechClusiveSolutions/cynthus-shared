# Project Instructions

This repository follows the Cynthus engineering standards in
[`cynthus-documentation/docs/engineering-standards.md`](https://github.com/TechClusiveSolutions/cynthus/blob/dev/docs/engineering-standards.md).
The rules that matter most:

- **A GitHub issue exists before any work with a deliverable starts.** Set its Issue Type, milestone, priority, subtype,
  "Applies to" and estimated completion, add it to the *Cynthus Engineering Tracker* project
  (<https://github.com/orgs/TechClusiveSolutions/projects/6>), and move it to `In Progress`.
- **Branch with `gh issue develop <number> --base dev`.** Feature branches merge into `dev`; `dev` merges into `main`.
  No direct commits to either.
- **One class per module, one unit test module per source module.**
- **Lint and tests must pass** (`ruff check .`, `python -m pytest --cov=src --cov-branch --cov-report=json` and `python .github/scripts/check_coverage.py`) before a pull request
  merges. Request GitHub Copilot as a reviewer and address its feedback.
- Pull requests use the template in `.github/pull_request_template.md` and contain `Closes #<issue>`.
- Never commit secrets. `.env` files stay untracked.
