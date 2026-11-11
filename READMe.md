# cynthus-shared

The library every Cynthus service imports as `cynthus`: the signal contracts (`cynthus.messaging`), the Redis and logging helpers (`cynthus.core`), and token issuing and verification (`cynthus.security`). It is not a service. The documentation is in [docs](docs).

## Releases

Services install this library from a release tag, never from a branch:

```text
git+https://github.com/TechClusiveSolutions/cynthus-shared@v0.1.0
```

A tag names exactly the code a service was built and tested with. Because the pin lives in the service's `requirements.txt`, Docker rebuilds the pip layer exactly when the pin changes, so a new release always reaches the image.

| Branch or tag | Meaning |
|---|---|
| `dev` | Merged work. CI in the service repositories tests against it. |
| `main` | Promoted from `dev` with a merge commit (never squashed, so the branches do not diverge). |
| `vX.Y.Z` | A release: a tag on `main`. |

### Cutting a release

1. Open a pull request from `dev` into `main`, wait for CI, and merge it with a **merge commit**. Do not delete `dev`.
2. Tag the new `main` commit with the next version: `git tag vX.Y.Z origin/main && git push origin vX.Y.Z`. While the library is young, a new signal or class is a minor version (`v0.2.0`) and a fix is a patch (`v0.1.1`).
3. In each service repository, change the pin in every `requirements.txt` that names `cynthus-shared` to the new tag, and open a pull request. A service that needs the new release cannot merge before it is tagged.
4. Rebuild the images that changed (`docker compose build <service>`); no `--no-cache` is needed once the pin has changed.

Never move or delete a published tag. A bad release is replaced by a new patch version.

### Releases so far

| Tag | Adds |
|---|---|
| `v0.1.0` | The JWT classes in `cynthus.security`, the identity audit signals, the inventory request and response signals, and the shared signal publisher that keeps one sender open. |
| `v0.11.0` | A RabbitMQ signal broker (`RabbitMqSignalPublisher`, `RabbitMqSignalSubscriber`) beside Service Bus, chosen by `SIGNAL_BROKER`, and the `SignalBroker` factory that `ServiceApplication` uses. Every release is listed in `CHANGELOG.md`. |
| `v0.11.1` | A RabbitMQ broker that is reconnecting is reported as `SignalBusUnavailable`, so a request gets the 503 answer instead of a 500. |
| `v0.12.0` | `ServiceApplication` can host several domain services in one process (`ServiceModule`, `modules=[...]`) over one broker connection, with per-module signal health, and a handler time limit (`SIGNAL_HANDLER_TIMEOUT_SECONDS`, default 60). |
| `v0.13.0` | The core model classes in `cynthus.core` (users, tenants with parents and billing accounts, workspaces, service identities, resources, events), pure data in one layout, with defaults, shelf fill orders, soft deletes, external accounts, and test factories and fixtures for every class. The tests moved to `test/unit/cynthus`. |
