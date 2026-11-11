# Changelog

All notable changes to cynthus-shared are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the versions follow
[Semantic Versioning](https://semver.org/). The Cynthus ecosystem release that bundles
each version is listed in the `cynthus` documentation repository.

Every pull request adds a line under `Unreleased`; a release renames that section to the
version and date.

## [Unreleased]

- Nothing yet.

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
