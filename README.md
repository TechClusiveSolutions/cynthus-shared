# cynthus-shared

## Description

The library every Cynthus service imports as `cynthus`: the signal contracts (`cynthus.messaging`), the Redis and
logging helpers (`cynthus.core`), token issuing and verification (`cynthus.security`) and the service application
(`cynthus.service`). It is not a service: there is nothing to run.

## Prerequisites

- Python 3.11 or later.
- Git, to install from a release tag.

## Installation

Pin a release tag in the service's `requirements.txt`, never a branch:

```text
git+https://github.com/TechClusiveSolutions/cynthus-shared@v0.17.0
```

To work on the library itself:

```sh
git clone https://github.com/TechClusiveSolutions/cynthus-shared.git
cd cynthus-shared
pip install -r requirements-dev.txt
python -m pytest
```

## Minimal configuration

None for the library. The settings belong to the services that use it; the signal broker choice (`SIGNAL_BROKER`,
`RABBITMQ_URL`, `SERVICE_BUS_CONNECTION_STRING`) is described in
[`docs/cynthus/messaging/broker.md`](docs/cynthus/messaging/broker.md).

## Gotchas

- A tag names exactly the code a service was tested with. Never move or delete a published tag; a bad release is
  replaced by a new patch version.
- `main` is promoted from `dev` with a merge commit, never squashed, so the branches do not diverge.
- A service that needs a new release cannot merge its pin change before the tag exists.
- The library imports its public classes from `__init__.py`; add new ones there.

## More documentation

- [`docs/creating-a-service.md`](docs/creating-a-service.md): how to add a new service, step by step.
- [`docs/releases.md`](docs/releases.md): how to cut a release, and what each release added.
- [`docs/cynthus/messaging/index.md`](docs/cynthus/messaging/index.md): signals, topics, subscriptions and the broker.
- [`docs/cynthus/security/index.md`](docs/cynthus/security/index.md): tokens and permissions.
- [`docs/cynthus/core/index.md`](docs/cynthus/core/index.md): the core model, Redis and logging helpers.
- [`docs/cynthus/service/index.md`](docs/cynthus/service/index.md): the shared service application.
- [`CHANGELOG.md`](CHANGELOG.md): what changed in each release.
- [Engineering standards](https://github.com/TechClusiveSolutions/cynthus/blob/dev/docs/engineering-standards.md):
  branches, tests, lint and review.
