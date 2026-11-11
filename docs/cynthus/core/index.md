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

| Package | Classes |
|---|---|
| `cynthus.core.user` | `User` |
| `cynthus.core.system` | `System` (fixed identity and the version), `Tenant`, `TenantType`, `Workspace`, `BillingAccount` |
| `cynthus.core.service` | `Service`, `ServiceDomain`, and one identity per service: `InventoryService`, `ProfileService`, `ShoppingService`, `LogisticsService`, `RecipeService` |
| `cynthus.core.resource` | `Resource`, `WorkspaceResource`, `Item`, `StorageLocation`, `StorageShelf` and the join records |
| `cynthus.core.event` | `Event`, `UserEvent`, `SystemEvent`, `EventRequest`, `EventRequestResponse` and its decision classes |

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

## Events

An `Event` is an action (`EventAction`) taken on a `Resource` in a tenant and workspace, with a `correlation_id`, the time it `occurred_on`, free-form `data` and the `service_id` that recorded it. A `UserEvent` adds the `user`; a `SystemEvent` carries the `System`. An `EventRequest` asks for an event to be allowed (the requestor is a `User` or the `System`), and an `EventRequestResponse` records the decision (`approve`, `deny` and the two conditional forms), naming the service that decided.

---

## Version

`cynthus.__VERSION__` is the release of cynthus-shared this code belongs to and is what `System().version` reports. A release changes it in the same pull request that dates the change log; a test fails if they differ.
