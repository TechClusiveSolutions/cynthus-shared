# Subscription Classes

Each service that consumes from `cynthus-events-topic` has a dedicated subscription class. All concrete subscription classes extend `PublicSubscription`, which extends FastStream's `AzureServiceBusSubscription`.

A subscription class's only responsibility is to declare the correct queue name for its service. The topic binding is handled by `PublicSubscription`.

---

## `PublicSubscription`

**Module:** `cynthus.messaging.subscription.public_subscription`

The abstract base for all public-topic subscriptions. Not used directly - subclass it for each consuming service.

```python
class PublicSubscription(AzureServiceBusSubscription):
    def __init__(self, *, name: str, **kwargs) -> None:
        super().__init__(name=name, topic=PublicTopic(), **kwargs)
```

**Topic:** `cynthus-events-topic` (via `CoreSignalTopic`, aliased as `PublicTopic`)

---

## Concrete subscription classes

- `AnalysisPublicSubscription`
  - Module: `subscription.analysis_public_subscription`
  - Queue name: `cynthus-analysis-public-sub`
  - Consuming service: `cynthus-analysis`
- `AuditPublicSubscription`
  - Module: `subscription.audit_public_subscription`
  - Queue name: `cynthus-audit-public-sub`
  - Consuming service: `cynthus-audit`
- `BillingApiPublicSubscription`
  - Module: `subscription.billing_api_public_subscription`
  - Queue name: *(see source)*
  - Consuming service: `cynthus-billing-api`
- `ChatPublicSubscription`
  - Module: `subscription.chat_public_subscription`
  - Queue name: `cynthus-chat-public-sub`
  - Consuming service: `cynthus-chat`
- `CoreApiSignalSubscription`
  - Module: `subscription.core_api_signal_subscription`
  - Queue name: `cynthus-sub-core-api`
  - Consuming service: `cynthus-core-api`
- `CoreCachePublicSubscription`
  - Module: `subscription.core_cache_public_subscription`
  - Queue name: *(see source)*
  - Consuming service: `cynthus-core-cache`
- `HealthApiPublicSubscription`
  - Module: `subscription.health_api_public_subscription`
  - Queue name: *(see source)*
  - Consuming service: `cynthus-health-api`
- `IdentityPublicSubscription`
  - Module: `subscription.identity_public_subscription`
  - Queue name: *(see source)*
  - Consuming service: `cynthus-identity`
- `MessagingPublicSubscription`
  - Module: `subscription.messaging_public_subscription`
  - Queue name: *(see source)*
  - Consuming service: `cynthus-messaging`
- `NotificationPublicSubscription`
  - Module: `subscription.notification_public_subscription`
  - Queue name: *(see source)*
  - Consuming service: `cynthus-notification`
- `PartnerApiPublicSubscription`
  - Module: `subscription.partner_api_public_subscription`
  - Queue name: *(see source)*
  - Consuming service: `cynthus-partner-api`
- `ProfilePublicSubscription`
  - Module: `subscription.profile_public_subscription`
  - Queue name: `cynthus-profile-public-sub`
  - Consuming service: `cynthus-profile`
- `RecipePublicSubscription`
  - Module: `subscription.recipe_public_subscription`
  - Queue name: `cynthus-recipe-public-sub`
  - Consuming service: `cynthus-recipe`
- `SchedulerPublicSubscription`
  - Module: `subscription.scheduler_public_subscription`
  - Queue name: *(see source)*
  - Consuming service: `cynthus-scheduler`
- `ShoppingPublicSubscription`
  - Module: `subscription.shopping_public_subscription`
  - Queue name: *(see source)*
  - Consuming service: `cynthus-shopping`

> Several subscription classes are stubs with queue names not yet populated. These are tracked for completion as services are implemented.

---

## Usage in a service

Instantiate the subscription class in the service's FastStream broker setup, then register handlers against it:

```python
from cynthus.messaging.subscription import RecipePublicSubscription

subscription = RecipePublicSubscription()

@broker.subscriber(subscription)
async def handle_meal_tag_created(message: MealTagCreatedMessage) -> None:
    ...
```

---

## Adding a subscription for a new service

1. Create `{service_name}_public_subscription.py` in `src/cynthus/messaging/subscription/`.
2. Subclass `PublicSubscription` and pass the queue name as `name`.
3. Export the class from `subscription/__init__.py`.

Queue names follow the convention `cynthus-{service-name}-public-sub`.

```python
class MyServicePublicSubscription(PublicSubscription):
    def __init__(self, **kwargs) -> None:
        super().__init__(name='cynthus-my-service-public-sub', **kwargs)
```

> **Note:** `CoreApiSignalSubscription` uses a slightly different naming convention (`cynthus-sub-core-api` rather than `cynthus-core-api-public-sub`). New subscriptions should follow the standard `cynthus-{service}-public-sub` pattern.
