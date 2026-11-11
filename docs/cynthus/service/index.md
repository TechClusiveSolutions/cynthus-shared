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
