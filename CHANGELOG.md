# Changelog

All notable changes to cynthus-shared are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the versions follow
[Semantic Versioning](https://semver.org/). The Cynthus ecosystem release that bundles
each version is listed in the `cynthus` documentation repository.

Every pull request adds a line under `Unreleased`; a release renames that section to the
version and date.

## [Unreleased]

- Guide to creating a new service (issue 143): `docs/creating-a-service.md`, modelled on the Analysis service, linked from the README and the service index.
- README follows the standard quick-start structure (issue 141; cynthus#57): Description, Prerequisites, Installation, Minimal configuration, Gotchas, More documentation. The longer sections moved unchanged into `docs/`. `check_markdown.py` now checks the README headings.
- Documentation for screen readers (issue 139): Markdown is ASCII only, has no tables (lists instead), names the language of every code block, and `README.md` has the standard name. `.github/scripts/check_markdown.py` now enforces this, and checks that relative links resolve, in the `docs-lint` job; markdownlint covers every Markdown file. The message documentation's tree diagrams became lists; the field tables became nested lists.

## [0.17.0] - 2026-11-12

- Added the `auth` signal domain and the signals `public.auth.workspace_role.created` and `public.auth.workspace_role.updated`, with their messages and payloads (`AuthWorkspaceRoleCreatedMessage`, `AuthWorkspaceRoleUpdatedMessage`). Auth publishes them when a request for access is made and answered (ADR-013, #135).

## [0.16.0] - 2026-11-12

- Tokens with the nil workspace id are refused (issue 131): `RequirePermission` answers `409` with `{"error": ..., "code": "workspace_required"}` after the permission check and records a rejected decision; `SignalAccess.authorize` refuses it too (`Forbidden('workspace_required')`). New: `TokenClaims.has_workspace`, `NO_WORKSPACE`, and an optional `code` on `AccessDenied` that the error envelope carries.

## [0.15.0] - 2026-11-12

- The decision model of ADR-013 in `cynthus.core.event`: an `EventRequest` has an `id_` and `in_reply_to`; `EventRequestResponse` keeps every decision (`decisions`, with `decision` the latest and `in_effect`) instead of one; `EventRequestDecision.reason` is now `answer_reason` (plain text, with the shared words in `EventRequestAnswerReason`, renamed to `approval_required`, `approval_granted`, `approval_denied` and gaining `expired`); the single condition is replaced by `DecisionCondition` records with a status, an `expires_at` and an exact-match test against a reply's answer reason (`settle`, `expire`). Factories, fixtures and docs follow. Breaking for code that used `EventRequestDecision.reason`, `EventRequestDecisionReason` or `EventRequestDecisionCondition` (nothing in the services does). Issue 127.

## [0.14.0] - 2026-11-12

- `ServiceModule` takes the `Service` identity (ADR-009 step 2): `ServiceModule(service=InventoryService(), ...)` takes its name from the service, refuses a different name, and the signal health names the service by `service_id`. A module without a service works as before. Issue 119.
- `tenant_id` beside `organization_id` in every signal and access token (ADR-010 step 1): the same value under both names; either may be given, both are written, and two different values are refused; old signals and tokens that carry only `organization_id` still read, and so do ones with only `tenant_id`. `TokenClaims.tenant_id` is new. `organization_id` is deprecated and goes after one release. Issue 120.
- `Engagement`, `Place` and `Attendee` in the core model (ADR-011): an engagement has a time period that must end after it starts, an optional place of its own workspace (else the workspace's default place, of which there is at most one), attendees with food preferences, managers, materials and notes. Factories and fixtures included. Data classes only; no database yet. Issue 121.

## [0.13.0] - 2026-11-12

- The core model classes (issue 93): `cynthus.core` now holds the classes that describe the ecosystem in one consistent layout: `User`, `System`, `Tenant`, `Workspace`, `BillingAccount`, the `Service` identities (`InventoryService`, `ProfileService`, `ShoppingService`, `LogisticsService`, `RecipeService`), `Resource` and its storage and item classes, and `Event`, `EventRequest` and `EventRequestResponse` with their decision classes. They are pure data (no web framework, database or broker; a test checks it) and serialize with pydantic. A `Tenant` can have a parent: a bridge tenant with the same owner and no workspaces, and a tenant is billed to one of its owner's billing accounts (ADR-010). A service builds the events and requests it records and the event names it in `service_id` (ADR-009). `cynthus.__VERSION__` is now the release in this change log and a test keeps them equal. Documented in `docs/cynthus/core/index.md`. Fixed on the way: `InventoryService.build_event` raised `NameError`, `EventRequestDecision` could not be created, and `EventRequestResponse` could not be built without a decision. Issue 93.
- Defaults, fill order and soft deletes in the core model (ADR-011): `is_default` on storage locations and shelves, a `fill_order` on shelves (`ShelfFillOrder`, eight values, default `back_left_horizontal`), and `SoftDeletable` (`deleted_at`, `soft_delete`, `restore`) on users, tenants, workspaces, billing accounts, resources and the join records. `User.external_accounts` (`ExternalAccount`: provider and subject), empty for a user created directly and set for one created through the Auth0 integration. Test factories and pytest fixtures for every core class (`cynthus.core.test`), documented in `docs/cynthus/core/index.md`. The tests moved from `test/cynthus` to `test/unit/cynthus`. Issue 93.

## [0.12.0] - 2026-11-12

- `ServiceApplication` can host several domain services in one process (ADR-008, step 1): `ServiceApplication(name, modules=[ServiceModule(...), ...])` opens Redis, the token verifier and the broker once, subscribes every module and runs one subscriber. `/signal/health` lists the modules and answers 503 if any is unavailable, and `/signal/health/{module}` answers for one. The single-module arguments work unchanged. New `ServiceModule` class. New setting `SIGNAL_HANDLER_TIMEOUT_SECONDS` (default 60, `0` for no limit): a handler that runs longer is cancelled and its signal dead-lettered, for every service. Issue 112.

## [0.11.1] - 2026-11-11

- Fixed: with RabbitMQ stopped, a request that published a signal got a 500 instead of the 503 Service Unavailable answer. While the broker connection reconnects, `aio_pika` raises a bare `RuntimeError`; `RabbitMqConnection.channel()` now reports it as a `ConnectionError`, so the publisher raises `SignalBusUnavailable` and the outage flag is set. Found in the whole-stack run on RabbitMQ (core 183). Issue 108.

## [0.11.0] - 2026-11-10

- Added a RabbitMQ broker behind the existing `SignalPublisher` and `SignalSubscriber` interfaces, chosen by the `SIGNAL_BROKER` setting (`servicebus` by default, `rabbitmq` or `memory`) with `RABBITMQ_URL` for the connection. `RabbitMqSignalPublisher` waits for the broker's confirmation and keeps the same 5-second attempt limit, 15-second cool-down and `SignalBusUnavailable` behaviour as the Service Bus publisher. `RabbitMqSignalSubscriber` reads one quorum queue per subscription, acknowledges what the handler accepts and dead-letters what it raises on, with the same delivery limit (10) and one-hour TTL as the emulator configuration. A process holds one broker connection, so the emulator's ten-connection cap no longer limits the stack when RabbitMQ is used. A new `SignalBroker` builds the publisher, subscriber and connection for the chosen broker and `ServiceApplication` now uses it, so services no longer name Service Bus. Behaviour with `SIGNAL_BROKER` unset is unchanged. Documented in `docs/cynthus/messaging/broker.md`; design in ADR-007 (cynthus docs repo, issue 34). Issue 103.

## [0.10.0] - 2026-11-08

- Bound the wait for an unreachable bus and share the outage through a Redis flag (#97) (#98)

## [0.9.0] - 2026-11-08

- SignalBusUnavailable, and a 503 answer for a request that failed because the bus is down (#94) (#95)

## [0.8.0] - 2026-11-08

- ServiceApplication: readiness health, optional bus, startup/shutdown hooks (#87) (#91)

## [0.7.0] - 2026-11-08

- SignalAccess reads the token from a ReceivedSignal as well as a Service Bus message (#87) (#89)
- Add ServiceApplication and ServiceBusConnection for the shared service startup (#87) (#88)

## [0.6.0] - 2026-11-08

- Name the Scheduler subscription cynthus-sub-scheduler, without "core" (#84) (#85)

## [0.5.0] - 2026-11-08

- Add the Service Bus signal subscriber and the received-signal type (#79) (#82)
- Add the signal publisher interface and the Service Bus publisher behind it (#79) (#80)

## [0.4.6] - 2026-11-08

- Add the shopping list request and response signals (#78)

## [0.4.5] - 2026-11-08

- Add the shopping list and list item signals (#75) (#76)

## [0.4.4] - 2026-11-07

- Add the user registered and email verified identity signals

## [0.4.3] - 2026-11-06

- Add the recipe request, response and fact signals (#65) (#66)

## [0.4.2] - 2026-11-06

- Send one signal at a time so overlapping publishes cannot leak connections (#63)

## [0.4.1] - 2026-11-05

- Add the intelligence and analysis domains and the chat and compute actions (#58)

## [0.4.0] - 2026-11-05

- Declare sqlalchemy[asyncio] as a dependency of the package (#53)
- Add the inventory owner added and removed signals (#52)

## [0.3.1] - 2026-11-05

- Make RedisClient recover from dropped pooled connections (#45)

## [0.3.0] - 2026-11-05

- Add cynthus.service: shared request-handling classes and SignalConsumer (#41)

## [0.2.0] - 2026-11-05

- Document the release policy and steps (#35)
- Add profile request, response, fact, snapshot and hard-constraint audit signals (#38)

## [0.1.0] - 2026-11-05

- SignalPublisher keeps one sender open and shares one publisher per client (#32)
- Add inventory request and response signals for locations, shelves, items and owners (#31)
- Add SignalAccessRecorder that publishes the access audit signals (#30)
- Share the access dependency, token ids and a signal publisher (#26)
- Add identity audit signal classes (user, token and access) (#25)
- Add JWT issuing and verification classes (cynthus.security) (#21)
- Add inventory location, shelf and item signal classes (#18) (#19)
- Quiet the Azure SDK loggers by default
- Add cynthus.core.logging with a common default configuration (#15)
- Add cynthus.core.RedisClient with get, set, delete, publish and wait support (#13)
- Use plain-value subscriptions, emulator entity names and inventory list signals (#10)
- Adopt the Cynthus CI, lint and pull-request workflow (#1) (#5)
- Fix SignalMessage import on Python 3.11 and 3.12 (#6) (#7)
- Fix meal packages, add subscriptions and unit tests
- Initial commit
