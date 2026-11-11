# Service Classes (`cynthus.service`)

The small classes every service that answers requests with signals needs, so each service keeps only what is its own: its models, schemas, services and request handler. The Inventory, Profile and Auth services use them.

---

## Classes

| Class | Purpose |
|---|---|
| `ApiError` | A request that cannot be carried out, with an HTTP-style `status_code` and a `message`: 404 for something that does not exist, 409 for a conflict, 422 for bad input, 503 when the audit record could not be written. `ApiError.invalid(error)` turns a pydantic `ValidationError` into a 422 that names the first problem. |
| `Body` | `Body.validate(schema, data)` checks the data a request carries against a pydantic schema and raises `ApiError` (422); `Body.changes(body)` lists the fields that were sent and are not null. |
| `Identifier` | `Identifier.parse(value, name)` reads a UUID from text or a UUID and raises `ApiError` (422) when it is missing or malformed; `Identifier.optional` allows it to be absent. |
| `Outcome` | What came of a request: the `status`, a `result` or an `error`, and the `facts` to publish. |
| `Fact` | The message class, lifecycle and payload of a public fact that follows a successful change. |
| `Facts` | `Facts.publish(publisher, claims, fact)` publishes a fact for the caller's organization and workspace. A bus failure is logged and never raised: the change stands. |
| `Forbidden` | A `TokenError` that means 403 (the caller is known but not allowed) rather than 401. |
| `SignalAccess` | Checks that a signal was sent on behalf of a caller who may ask for it: the token forwarded in the `authorization` message property must be genuine, grant the permission, and name the same organization, workspace and actor as the signal. Tells an `AccessRecorder` about each decision. |
| `Database` | Async access to a service's database. The engine is created on first use, so importing a service never needs a database. `session()` returns an `AsyncSession`; `dispose()` closes the engine. |
| `DatabaseUrl` | Builds the SQLAlchemy URL (`postgresql+psycopg`) from `DB_HOST` (default `db`), `DB_PORT` (default `5432`), `DB_NAME`, `DB_USERNAME` and `DB_PASSWORD`. |
| `SignalConsumer` | The receiver loop every service that listens to the bus needs: `SignalConsumer(client, subscription_name, handler).run()` hands each message of the subscription to an async handler, completes it when the handler accepts it, dead-letters it when the handler raises, and stops on cancellation without settling the message in hand. |
| `SignalBroker` | The broker a process uses, chosen by `SIGNAL_BROKER` (`servicebus` by default, `rabbitmq` or `memory`). `SignalBroker.from_environment()` returns the `publisher`, the `subscriber` and the one shared connection (`client`); `close()` closes the publisher and then the connection. `ServiceApplication` uses it, so service code never names a broker. See `docs/cynthus/messaging/broker.md`. |
| `ServiceApplication` | The FastAPI application every domain service shares: it opens Redis, the token verifier and the broker, subscribes the service, runs the subscriber, adds `/` and `/signal/health`, and closes everything on shutdown. It hosts one module or several (see below). |
| `ServiceModule` | One domain service inside a `ServiceApplication`: `name`, `routers`, `subscription` and `handler` (given together), `signal_access`, `database`, `startup`, `shutdown` and `service`. `service` is the identity of the service (`cynthus.core.service.Service`, ADR-009); give it and the module takes its name from it (a different `name` is refused), and the health names the service by `service_id`. |

---

## A request handler in a service

A service's request handler is the only part that differs. The pattern:

```python
try:
    claims = await access.authorize(message, request, permission)   # SignalAccess
    outcome = await carry_out(claims, request.payload)               # raises ApiError
except Forbidden as error:
    outcome = Outcome(403, error=error.reason)
except TokenError as error:
    outcome = Outcome(401, error=error.reason)
except ApiError as error:
    outcome = Outcome(error.status_code, error=error.message)

await publisher.publish(response)                                    # the answer first
for fact in outcome.facts:
    await Facts.publish(publisher, claims, fact)                     # then the facts
```

## Listening to the bus

```python
consumer = SignalConsumer(service_bus_client, 'cynthus-analysis-sub', handle)
task = asyncio.create_task(consumer.run())
```

The subscription names are the ones in the emulator configuration (`cynthus-api-sub`, `cynthus-inventory-sub`, `cynthus-profile-sub`, `cynthus-analysis-sub`).

---

## Hosting several modules in one process

A deployable can host several domain services (ADR-008 in the `cynthus` documentation repository). Each is a `ServiceModule`; the application opens Redis, the token verifier and the broker once, subscribes every module on that one connection, and runs one subscriber:

```python
ServiceApplication(
    name='Domain',
    modules=[
        ServiceModule(service=InventoryService(), routers=[event], subscription=CoreInventorySignalSubscription(),
                      handler=handle_inventory, signal_access=inventory_access, database=inventory_database),
        ServiceModule(service=ProfileService(), ...),
    ],
).initialize()
```

- A service that passes `routers`, `subscription`, `handler` and the rest directly keeps working as before; give either `modules` or those arguments, not both. Module names must differ.
- Start-up hooks run in module order and shutdown hooks in reverse, then every database is disposed.
- `/signal/health` answers 200 only while the subscriber runs and every module's database answers. With several modules the body is `{"status": ..., "modules": {name: {...}}}`; `/signal/health/{module}` answers for one (404 for an unknown name). The subscriber is shared, so if it stops, every module is unavailable; the database check is per module.
- A handler that has not finished after `SIGNAL_HANDLER_TIMEOUT_SECONDS` (default 60; `0` means no limit) is cancelled and its signal is dead-lettered, so one slow module cannot hold up the others on the same event loop. A value that is not a number of seconds, 0 or more, stops the service at start-up.
