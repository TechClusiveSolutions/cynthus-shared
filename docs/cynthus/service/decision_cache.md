# DecisionCache (`cynthus.service.DecisionCache`)

Decisions are not stored per service (ADR-013). They are cached for a short time, so a retried request gets its earlier answer and an approval reply can find the decision it refers to.

---

## Use

```python
cache = DecisionCache(RedisClient.from_environment())

response = policy.decide(request, claims, permission='inventory.read', resource_tenant_id=tenant_id)
await cache.put(response)                       # never raises
await publisher.publish(event)

earlier = await cache.get(request.id_)          # EventRequestDecisionData or None
```

## What is cached

- The latest decision of the response, as `EventRequestDecisionData` (built by `EventRequestDecisionData.from_decision(request, decision)`, the same data the decision event carries), stored as JSON under `decision:<event_request_id>`. A response without a decision is not cached.
- The caller never builds or reads the JSON; the serialization lives in the cache and the data model.

## How long

- `ttl` (default 24 hours) for approved and denied decisions.
- For a decision with open conditions, the time left until the latest open condition expires, never shorter than `ttl`. A conditional approval waiting five days for an approval is cached for five days.
- `clock` (default: now, UTC) can be replaced in tests.

## Failures

- `put` logs a Redis or serialization error and returns; the decision still stands and is still published.
- `get` returns `None` for an unknown id, a corrupt cached value (logged) or a Redis error (logged).
