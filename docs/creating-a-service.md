# Creating a new service

How to add a service that listens to signals on the broker, modelled on the Analysis service in
[cynthus-intelligence](https://github.com/TechClusiveSolutions/cynthus-intelligence). Use it as the working example
and read its files beside this guide: `containers/analysis` and the `analysis` block of `docker-compose.yml`.

The shared pieces a service builds on (`ServiceApplication`, `ServiceModule`, `SignalAccess`, `SignalBroker` and the
rest) are described in [`cynthus/service/index.md`](cynthus/service/index.md).

---

## 1. Before you write code

- Open a GitHub issue in the repository that will hold the service, with its type, milestone, priority, size,
  subtype and "Applies to" set, and branch with `gh issue develop <number> --base dev`.
- Choose the repository. A service belongs in the repository of its segment (`cynthus-core`, `cynthus-trust`,
  `cynthus-intelligence`, `cynthus-health`). A segment with no repository yet needs a new one: create it, then run
  `python tools/bootstrap_repo.py <path-to-repo>` from the `cynthus` documentation repository to add the CI, lint
  and pull-request files, and write the README in the standard structure.
- Choose a short lower-case name, for example `analysis`. It becomes the package name, the container directory and
  the compose service name.
- Decide whether the service answers requests (a Core-style handler that checks a token and publishes an answer) or
  only listens (as Analysis does today).

## 2. The container directory

Create `containers/<name>/` with this layout (compare `containers/analysis`):

```text
containers/<name>/
  Dockerfile
  bin/startup.sh
  requirements.txt
  pytest.ini
  src/<name>/__init__.py
  src/<name>/signal_handler.py
  test/
```

- `Dockerfile`: starts `FROM ghcr.io/techclusivesolutions/cynthus-base:main`, installs `requirements.txt` with
  `/opt/python/bin/python3 -m pip`, exposes port 8000 and runs `/opt/app/bin/startup.sh`.
- `bin/startup.sh`: runs `exec /opt/python/bin/uvicorn <name>:app --host 0.0.0.0 --port "${PORT:-5000}"`. The file
  must be executable in git (mode `100755`); a file written on Windows loses the bit, and the container then exits
  with 126. Check with `git ls-files -s`.
- `requirements.txt`: pin `cynthus-shared` to a release **tag**, never a branch, and add what the service imports.
  Analysis lists `fastapi`, `uvicorn`, `redis`, `sqlalchemy[asyncio]`, `aio-pika`, `azure-identity` and
  `azure-servicebus`: the last two are needed because the default broker is Service Bus.
- One class per module, and one unit test module per source module (engineering standards, section 1).

## 3. The entry point

`src/<name>/__init__.py` builds the FastAPI application with the shared `ServiceApplication`:

```python
from cynthus.messaging.subscription.analysis_public_subscription import AnalysisPublicSubscription
from cynthus.service import ServiceApplication

from .signal_handler import handle_public_signal


def initialize():
    return ServiceApplication(
        name='Analysis',
        routers=[],
        subscription=AnalysisPublicSubscription(),
        handler=handle_public_signal,
    ).initialize()


app = initialize()
```

`ServiceApplication` opens Redis, the token verifier and the broker, subscribes the service, runs the subscriber,
adds `GET /` and `GET /signal/health`, and closes everything on shutdown. The service never names a broker: the
`SIGNAL_BROKER` setting chooses it.

## 4. The subscription

A service receives signals through a subscription named `cynthus-<name>-sub`.

1. Add a class to `cynthus-shared`, in `src/cynthus/messaging/subscription/<name>_public_subscription.py`, that
   subclasses `PublicSubscription` and passes the name (see `analysis_public_subscription.py`). Add a unit test for
   it, a line in the changelog, and cut a release (see [`releases.md`](releases.md)).
2. Move the service's `requirements.txt` pin to that release.
3. For the Service Bus emulator, add the subscription to
   `containers/messaging/conf/Config.json` in `cynthus-emulators`, then restart the emulator and every service
   that connects to it. RabbitMQ needs nothing: each service declares its own exchange, queue and dead-letter queue
   when it starts.

## 5. The signal handler

`src/<name>/signal_handler.py` holds one async function, `handle(signal, publisher)`, called for each signal. It
reads the body against its message contract (for example `ProfileSnapshotPublishedMessage.model_validate_json`), so
a malformed signal is refused, and it acts on the event type it cares about.

- If the handler raises, the signal is dead-lettered (queue `<subscription>.dlq` on RabbitMQ). A handler that has
  not finished after `SIGNAL_HANDLER_TIMEOUT_SECONDS` (default 60) is cancelled and dead-lettered too.
- Log the event type and the user, never the contents of a signal: profile signals hold allergies and medical
  conditions.
- A service that answers requests also uses `SignalAccess` to authorize the caller, builds an `Outcome`, publishes
  the answer first and then the `Fact`s, as in the pattern in the service index.

## 6. Compose

Copy the `analysis` block of `docker-compose.yml` and change the names. It sets, for the container:

- `TZ`, `PYTHONPATH=/opt/app/shared/src:/opt/app/src` and `PYTHONUNBUFFERED=1`;
- `CACHE_HOST`, `CACHE_PORT`, `CACHE_USERNAME` and `CACHE_PASSWORD`, and `PORT`;
- `SIGNAL_BROKER` (default `servicebus`) and `RABBITMQ_URL`, `SERVICE_BUS_CONNECTION_STRING` and
  `SERVICE_BUS_NAMESPACE`;
- for a service that checks tokens, `AUTH_JWKS_URL`, `AUTH_ISSUER` and `AUTH_AUDIENCE` (see the core services);
- bind mounts of `bin`, `src` and `test` for development, an `expose` of the port (nothing is published to the
  host), the `net` network (and the internal `vnet` if it uses the segment's database or cache), and a health check
  that calls `GET /`.

## 7. Tests

- The conftest and `pytest.ini` are generated: add the container to the `CONTAINERS` table in
  `tools/generate_service_tests.py` in the `cynthus` documentation repository and run the generator. Edit the
  generator, never the generated files.
- Write a test for the signal handler that fails without it, with a fake publisher and a signal built from the real
  contract classes.
- `python -m pytest --cov=src --cov-fail-under=75` and `ruff check .` must pass.
- Service containers run Python 3.11. Run the tests in the service image as well as on your machine, because code
  that passes on a newer Python can fail in the container.

## 8. Check that it works

```sh
docker compose up -d --build <name>
docker compose ps
```

The container is `healthy` when `GET /` answers. `GET /signal/health` answers 200 only while the subscriber runs.
Send a signal of a type the service handles and look for its log line.

Before the pull request: a `CHANGELOG.md` line, the README (standard structure) and `docs/` updated, markdown checks
clean, and `Closes #<issue>` in the description.

## Gotchas

- A broker setting must match in every stack, or signals will not cross between services on different brokers.
- The Service Bus emulator has a small connection limit (10 by default) that a full stack can exceed; every new
  service adds a connection. RabbitMQ has no such limit.
- A pin to an old `cynthus-shared` tag still works but misses newer behaviour. Analysis pins an earlier tag than the
  rest of the platform, so check the latest release before you copy its `requirements.txt`.
- A new signal or subscription needs a shared release first, then the pin change in the service; the service cannot
  merge before the tag exists.
