# Core model classes (`cynthus.core`)

The classes that describe the things in Cynthus: who a user is, what a tenant and a workspace are, which service acted, what a resource is, and what happened to it. They are plain pydantic models, laid out the same way everywhere, so a thing looks the same to every service and every repository that uses it. The decisions behind them are ADR-009 (the Service object) and ADR-010 (tenants) in the `cynthus` documentation repository.

**These classes are pure data.** They import no web framework, database or broker (`fastapi`, `sqlalchemy`, `azure`, `aio_pika`, `cynthus.service`, `cynthus.messaging`), so any code can use them and they serialize with pydantic (`model_dump(mode='json')`, `model_validate_json`). The runtime side of a service lives in `cynthus.service` and imports these, never the reverse. A test enforces it (`test/unit/cynthus/core/test_layering.py`).

---

## The layout every class follows

- One class per file, named for the class, re-exported from the package `__init__.py`.
- Identity is `id_` (a UUID, `uuid4` by default). A class with one fixed identity (a service, the system) gives `id_`, `name` and the like a fixed default with `frozen=True`.
- Enumerations are `str` enums with lower-case values (`'personal'`, `'created'`).
- Timestamps are timezone-aware UTC.

---

## Packages

- `cynthus.core.soft_deletable`: `SoftDeletable`, the base of everything that holds a person's data
- `cynthus.core.user`: `User`
- `cynthus.core.system`: `System` (fixed identity and the version), `Tenant`, `TenantType`, `Workspace`, `BillingAccount`
- `cynthus.core.service`: `Service`, `ServiceDomain`, and one identity per service: `InventoryService`, `ProfileService`, `ShoppingService`, `LogisticsService`, `RecipeService`
- `cynthus.core.resource`: `Resource`, `WorkspaceResource`, `Item`, `Place`, `Engagement`, `Attendee`, `StorageLocation`, `StorageShelf`, `ShelfFillOrder` and the join records
- `cynthus.core.event`: `Event`, `UserEvent`, `SystemEvent`, `EventRequest`, `EventRequestResponse` and its decision classes

---

## Services

A `Service` is the identity of a service application: `id_`, `name`, `domain`. Each service has a fixed identity (`InventoryService().id_` is always `10000000-1000-1000-1000-100000000001`). A service builds the events it records and the requests for them:

```python
service = InventoryService()
event = service.build_event(tenant=tenant, workspace=workspace, resource=location,
                            action=EventAction.ADDED, user=user, data={'quantity': 2})
request = service.build_event_request(event, requestor=user, reason='stocking up')
```

The event carries `service_id`, the service that recorded it. `InventoryService` builds `InventoryEvent` and `InventoryEventRequest`; the others build the general classes. The running parts of a service (routers, subscription, handler, database) are joined to its identity by `ServiceModule` in `cynthus.service`.

---

## Tenants, parents and billing

A `Tenant` is the boundary of data ownership and access. It has a `type` (`personal` or `organizational`) and an `owner`.

- When one owner has several tenants, a **parent** ties them together. A parent is a tenant with `bridge=True`: it has the same owner as its children and **no workspaces** (`Workspace` refuses a bridge tenant). A child names it in `parent`.
- A tenant that has a parent must name a bridge tenant with the same owner; a bridge tenant cannot have a parent of its own. Each rule is checked when the object is built.
- A `BillingAccount` belongs to an owner and has its own `options`. `tenant.attach_billing_account(account)` bills the tenant to it (and refuses an account of another owner); several tenants may share one account.
- The owner of a tenant is a fact of the tenant, not a role. A token issued to someone else never carries owner rights; that check is Auth's, and is described in ADR-010.

---

## Defaults, fill order and soft deletes (ADR-011)

- A `StorageLocation` and a `StorageShelf` have `is_default`. A workspace has at most one default location and a location at most one default shelf; the database enforces it, and these classes only carry the flag.
- A `StorageShelf` has a `fill_order` (`ShelfFillOrder`): the corner the filling starts at and whether rows or columns come first. The default is `back_left_horizontal`.
- `SoftDeletable` gives `User`, `Tenant`, `Workspace`, `BillingAccount`, every `Resource` and the join records a `deleted_at`, `is_deleted`, `soft_delete(at=None)` (which returns the time, so what a thing holds can share it) and `restore()`. Every delete is a soft delete; only an explicit data-removal request removes data.

---

## Engagements and places

An `Engagement` is a gathering planned in a workspace: a time period (`starts_at`, `ends_at`; it must end after it starts), an optional `Place`, `attendees` with their food preferences, `managers`, the `materials` needed and logistical `notes`. A `Place` is a venue with an address and a capacity. A workspace has at most one default place (`is_default`, ADR-011); an engagement that names none uses it, and `engagement.place_or(default)` gives the place it uses. An engagement can only use a place of its own workspace. There are no tables for them yet; Logistics has no database.

---

## Events

An `Event` is an action (`EventAction`) taken on a `Resource` in a tenant and workspace, with a `correlation_id`, the time it `occurred_on`, free-form `data` and the `service_id` that recorded it. A `UserEvent` adds the `user`; a `SystemEvent` carries the `System`. An `EventRequest` asks for an event to be allowed (the requestor is a `User` or the `System`). It has an `id_` and may name the request it answers (`in_reply_to`), so an approval points at the request for access it approves.

An `EventRequestResponse` keeps the **decisions** made on a request (ADR-013). Decisions are only added, never changed: `decision` is the latest and `in_effect` says whether the request has taken effect. A decision has an `answer` (`approved`, `approved_conditionally`, `denied`, `denied_conditionally`), an `answer_reason` that says why the answer is what it is (`EventRequestAnswerReason`: `permitted`, `approval_required`, `approval_granted`, `approval_denied`, `insufficient_privileges`, `expired`, or a reason of a service's own such as `payment_method_linked`), the service that decided, and its **conditions**.

A `DecisionCondition` is what a conditional answer waits for. Its `condition` is the answer reason a reply must carry, and the test is an exact match: `reply.answer_reason == condition.condition`. `response.settle(reply_decision)` answers the open conditions: a matching reply satisfies the condition, a reply that denies fails it, any other leaves it open. A condition may have an `expires_at`; `response.expire(now)` expires the open ones that are due and adds a decision that denies the request with the answer reason `expired`, so expiry is recorded, not silent.

```python
access = EventRequestResponse(request=jills_request)
access.conditionally_approve('approval_required', [DecisionCondition(condition='approval_granted', expires_at=in_five_days)])

approval = EventRequestResponse(request=jacks_request)      # jacks_request.in_reply_to == jills_request.id_
access.settle(approval.approve('approval_granted'))          # the condition is met; access.in_effect is True
```

---

## Version

`cynthus.__VERSION__` is the release of cynthus-shared this code belongs to and is what `System().version` reports. A release changes it in the same pull request that dates the change log; a test fails if they differ.

---

## Test factories and fixtures

`cynthus.core.test.factory` has a factory for every class (`UserFactory`, `TenantFactory`, `BridgeTenantFactory`, `ChildTenantFactory`, `WorkspaceFactory`, `StorageLocationFactory`, `EventFactory` and the rest), and `cynthus.core.test.fixture` has a pytest fixture for each, named for the class in snake case (`user`, `bridge_tenant`, `storage_shelf`). Related objects are consistent: a workspace is owned by its tenant's owner, an event's workspace belongs to its tenant, and a child tenant has a bridge parent with the same owner. Import the fixtures you need into a `conftest.py`; a factory takes overrides (`UserEventFactory(tenant=my_tenant, data={...})`).

**Known limit:** an event holds its resource as the base `Resource`, so its JSON loses the fields of the real kind (a location's type, a shelf's slots). A test marks it as an expected failure; a tagged union on the resource would fix it.
