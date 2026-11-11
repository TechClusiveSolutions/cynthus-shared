# Choosing the signal broker

A process publishes and subscribes through the `SignalPublisher` and `SignalSubscriber` interfaces. Which broker sits behind them is an environment setting, so the same service image runs against Azure Service Bus, against RabbitMQ, or with no broker at all. The decision and its reasons are in ADR-007 in the `cynthus` documentation repository.

---

## Settings

| Variable | Meaning |
|---|---|
| `SIGNAL_BROKER` | `servicebus` (the default), `rabbitmq` or `memory`. Blank means `servicebus`. Anything else stops the service at start-up and names the choices. |
| `SERVICE_BUS_CONNECTION_STRING` | Service Bus only. The emulator connection string. Without it, `SERVICE_BUS_NAMESPACE` and Azure credentials are used. |
| `RABBITMQ_URL` | RabbitMQ only. `amqp://user:password@host:5672/vhost`. It is a secret: keep it in the untracked `.env`, never in a repository or a log. |

`memory` keeps every signal inside the process (`InMemorySignalBus`). It is for unit tests and local runs of one service.

---

## How a service gets its broker

Service code never names a broker. `ServiceApplication` asks `SignalBroker.from_environment()` (in `cynthus.service`) for the pieces:

| Attribute | What it is |
|---|---|
| `publisher` | The process's `SignalPublisher`. It has an `on_unavailable` hook and a `close()`. |
| `subscriber` | The process's `SignalSubscriber`: `subscribe(topic, subscription, handler)` and `run()`. |
| `client` | The one connection both share (the Service Bus client, or the `RabbitMqConnection`). |

A service that builds its own publisher (the Core API, Auth, the Celery services) should use `SignalBroker` the same way instead of constructing `ServiceBusSignalPublisher` directly.

---

## What every broker must do

- `publish` returns only after the broker has accepted the message, and raises `SignalBusUnavailable` when it cannot. Each attempt waits at most 5 seconds. After a failure the publisher refuses at once for 15 seconds and calls `on_unavailable`, which is how `ServiceOutage` and the Service Unavailable page learn of the outage.
- The caller's token travels beside the body as the `authorization` property (a header on RabbitMQ), never inside the body, and is never logged.
- A handler that returns settles its signal. A handler that raises sends the signal to the dead-letter queue, and the signals behind it are not blocked.
- Cancelling `run()` stops delivery and leaves the signals in hand unsettled, so the broker delivers them again.
- A process holds one broker connection. While the broker is away the connection reconnects by itself; a publish made meanwhile raises `SignalBusUnavailable` (so the caller gets the 503 answer), and publishing works again as soon as the broker returns.

---

## RabbitMQ topology

Use RabbitMQ 4.x. Each service declares what it needs when it starts; the declarations are idempotent, so nothing has to be created by hand.

| Service Bus | RabbitMQ |
|---|---|
| Topic `cynthus-events-topic` | A durable topic exchange of that name |
| Event type, for example `audit.identity.user.rejected` | The routing key, and the message's `type` property |
| Subscription, for example `cynthus-profile-sub` | A durable quorum queue of that name, bound to the exchange with `#` |
| Complete | Ack |
| Dead-letter | Reject without requeue, to the direct exchange `cynthus-events-topic.dlx`, which routes to the queue `<subscription>.dlq` |
| `MaxDeliveryCount` 10 | `x-delivery-limit` 10 |
| TTL one hour | `x-message-ttl` 3,600,000 ms |
| Message properties | `message_id`, `correlation_id`, `content_type`, and the `authorization` header |

To look at a dead letter, open `<subscription>.dlq` in the RabbitMQ management page and get its messages; the `x-death` header says which queue it came from and why.

Redeclaring a queue with different arguments fails in RabbitMQ. If you change the delivery limit or the TTL, delete the old queue or rename the subscription; the subscriber reports this with a message that names the queue.

RabbitMQ has no scheduled enqueue, sessions, duplicate detection or lock renewal. No Cynthus service uses them. Idempotency stays in the services (`processed_requests`).

---

## Testing

Unit tests run without a broker: `aio_pika` is imported only when the RabbitMQ connection is used, and the tests replace it with a fake (`test/cynthus/messaging/conftest.py`). The tests under `test/integration` run against a real RabbitMQ and are skipped unless `RABBITMQ_URL` is set:

```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4-management
RABBITMQ_URL=amqp://guest:guest@localhost:5672/ python -m pytest test/integration -q
```

A service that runs only on Service Bus does not need `aio-pika` installed. A service that sets `SIGNAL_BROKER=rabbitmq` does.
