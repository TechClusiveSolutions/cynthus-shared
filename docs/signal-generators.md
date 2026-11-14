# Signal generators

A signal generator turns one event into one signal message. A publisher only sends messages.

## Event, signal and generator

- An event is a logical unit in the core data layer. It says what happened.
- A signal is the announcement of an event: a message with a name, an envelope (who, what, when, where) and a body (why
  and how). Signals tell consumers which events were generated. A signal name is `visibility.domain.aggregate.action`,
  for example `public.inventory.shelf.created`.
- A signal generator composes the message of one event. A resource generator, such as `InventoryShelfSignalGenerator`,
  fills only the body. The base class `SignalGenerator` builds the envelope once, in `envelope`.
- Messaging depends on core events. Nothing under `cynthus.core` imports from `cynthus.messaging`.
- The `event_type` of a message is the signal name. The `event_type` of an event is the snake_case of its class name
  without a trailing `Event`; it equals the signal name without its visibility, with dots replaced by underscores.

## The purity rule

A generator is a pure function of the event: no I/O, no lookups, no clock, no random ids and no change to the event. The
same event always gives an equal message. The message `event_id` is the id of the event, and its `timestamp` and the
payload `observed_at` are `event.occurred_on`. Everything else a signal needs travels in the event. If a payload field
needs data, the data model of the event must carry it.

An event class may declare `data_model`, a pydantic model. The event checks `data` against it when it is created, so a
missing field fails where the event is made, not at publish time.

## Publishing an event

```python
publisher = EventMessagePublisher(transport=RabbitMqSignalPublisher(...))
message = await publisher.publish(event, access_token, topic=topic)
```

`EventMessagePublisher` wraps any `SignalPublisher`. It finds the generator in a `SignalGeneratorRegistry`, generates
the message, hands it to the transport and returns it. A lookup or generation error propagates and nothing is sent.
`UnknownEventError` means no generator is registered for the event. Code that already holds a message calls the
transport directly.

## Adding a signal

The signal, message and payload classes are described in
[`docs/cynthus/messaging/index.md`](cynthus/messaging/index.md) and, for inventory, in
[`docs/cynthus/messaging/component/inventory/shelf.md`](cynthus/messaging/component/inventory/shelf.md) and its sibling
pages. Create them first; this page covers the event and the generator.

1. Choose the registry key. It is the exact class name of the event, for example `InventoryShelfCreatedEvent`. A
   mistyped name never matches.
2. Add the event class and its data model in `src/cynthus/core/event/`, one class per module, and export both from
   `cynthus.core.event`.
3. Add the generator method and its `SignalContract` to the generator of the resource, or add a new generator class
   under `src/cynthus/messaging/component/<domain>/generator/` and add it to `SignalGeneratorRegistry.default()`.
4. Write a unit test module per source module: the event, its data model, the generator and, for a new one, its
   registration.
5. Write or extend the feature test in `test/integration/`. It starts at a real event and ends at a recording
   `publish()`, and asserts the whole message including the payload.
6. Add a CHANGELOG entry under Unreleased. Do not bump the version.

## Worked example: shelf created

The data model, in `src/cynthus/core/event/inventory_shelf_created_data.py`:

```python
class InventoryShelfCreatedData(BaseModel):
    """The data of an inventory shelf created event"""

    shelf_id: str
    location_id: str
    name: str
    position: int = 0
```

The event, in `src/cynthus/core/event/inventory_shelf_created_event.py`:

```python
class InventoryShelfCreatedEvent(InventoryEvent):
    """Represents the creation of an inventory shelf"""

    data_model: ClassVar[type[BaseModel] | None] = InventoryShelfCreatedData
```

The generator, in
`src/cynthus/messaging/component/inventory/generator/inventory_shelf_signal_generator.py`:

```python
class InventoryShelfSignalGenerator(SignalGenerator):
    """Generates the signals of an inventory shelf: ``public.inventory.shelf.created``"""

    contracts: ClassVar[tuple[SignalContract, ...]] = (
        SignalContract(
            features=('FT-IM-001',),
            event='InventoryShelfCreatedEvent',
            signal=PublicInventoryShelfCreatedSignal,
            message=InventoryShelfCreatedMessage,
            payload=InventoryShelfCreatedPayload,
            lifecycle_action=LifecycleAction.CREATED,
            method='created',
            sources={
                'shelf_id': 'data.shelf_id',
                'location_id': 'data.location_id',
                'name': 'data.name',
                'position': 'data.position',
            },
        ),
    )

    def created(self, event: Event) -> InventoryShelfCreatedMessage:
        """The message for a created shelf, from the data of the event"""

        contract = self.contract('created')
        data = InventoryShelfCreatedData.model_validate(event.data)
        payload = InventoryShelfCreatedPayload(
            shelf_id=data.shelf_id,
            location_id=data.location_id,
            name=data.name,
            position=data.position,
            observed_at=event.occurred_on,
        )

        return contract.message(**self.envelope(event, contract), payload=payload)
```

The generator class is listed in `SignalGeneratorRegistry.default()`. Publishing is then
`await EventMessagePublisher(transport).publish(event)`.

## The contract fields

A `SignalContract` is a frozen record. The chain from feature to field is feature, events, signal, payload fields and
the source of each field.

- `features`: Feature Registry ids, each matching `FT-XX-000`, for example `FT-IM-001`.
- `event`: the class name of the event.
- `signal`: the concrete signal class.
- `message`: the message class. Its default `event_type` must equal the signal name.
- `payload`: the payload class.
- `lifecycle_action`: the lifecycle action of the method (`CREATED`, `UPDATED`, `DELETED` and so on). Each method
  declares it; it is not derived from the event action.
- `method`: the name of the generator method.
- `sources`: maps every payload field name to a source expression. The expressions are `data.<field>` for the event
  data, `resource.<field>`, `user.<field>`, `tenant.<field>`, `workspace.<field>` and `env.<name>`.

The base fields that every payload has (`schema_version`, `observed_at`, `metadata`) need no source.

When a generator class is defined, `SignalGenerator` checks each contract and raises `TypeError` when:

- the method does not exist on the class;
- the default `event_type` of the message differs from the signal name;
- a payload field, other than the base fields, has no source;
- a source names a field the payload does not have;
- a source expression is malformed: it must be `data.`, `resource.`, `user.`, `tenant.` or `workspace.` plus a
  lower-case field name, or `env.` plus a name;
- the signal action is created, updated, deleted or snapshot and `lifecycle_action` differs from it;
- two contracts of the class share an event or a signal name.

`SignalGeneratorRegistry` also rejects an empty event name, a signal that is not a concrete signal class, an invalid
signal name, and a duplicate event or signal name across generators.

The drift tests over `SignalGeneratorRegistry.default().contracts()` check that each signal name is valid and unique,
that every source field under `data.` exists on the data model of the event, that each feature id matches the format,
that the event class exists in `cynthus.core.event`, and that its `event_type` equals the signal name without the
visibility prefix.

Not verified: that a `resource.`, `user.`, `tenant.`, `workspace.` or `env.` source names something that exists, that
the generator method really reads the source it declares, that the feature id exists in the Feature Registry, and that
the payload is equal to what the method builds. The feature test covers the message of each shipped signal.

## Signals that exist

All of them belong to FT-IM-001 and are in `SignalGeneratorRegistry.default()`:

- `InventoryShelfCreatedEvent` gives `public.inventory.shelf.created`
- `InventoryShelfUpdatedEvent` gives `public.inventory.shelf.updated`
- `InventoryShelfDeletedEvent` gives `public.inventory.shelf.deleted`
- `InventoryLocationCreatedEvent` gives `public.inventory.location.created`
- `InventoryLocationUpdatedEvent` gives `public.inventory.location.updated`
- `InventoryLocationDeletedEvent` gives `public.inventory.location.deleted`

Update events carry the ids and only the fields that changed. A field that did not change is left out of the event
data, and arrives in the payload as `None`. A value that is falsy but present, such as `0` or `False`, is a change and
is kept. An update that changes nothing is refused when the event is created, because it would announce nothing.
Delete events carry ids only.

## Example

```python
registry = SignalGeneratorRegistry.default()
registry.signal_for('InventoryShelfCreatedEvent').name
```

The result is `public.inventory.shelf.created`.
