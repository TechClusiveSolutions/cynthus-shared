# Decision policy

`DecisionPolicy` (`cynthus.service`) answers an event request the same way in every service, so a service does not write
its own access rules (ADR-013). It reads the verified token claims, never a database, and it reads the clock only to
date the expiry of an approval.

## Using it

```python
claims = await access.authenticate(message, signal_message)               # SignalAccess: genuine and matching, no permission yet
reader = SignalEventReader()
event = reader.read(signal_message, claims, PartnerServiceListRequestedEvent)
request = EventRequest(event=event, requestor=claims.subject)
policy = DecisionPolicy(determined_by=service_id)
response = policy.decide(request, claims, permission='partner:read', resource_tenant_id=resource.tenant_id)

if response.in_effect:
    ...                                                              # carry the request out
```

`SignalAccess.authenticate(message, signal_message)` does what `authorize` does, except that it does not ask for a
permission: it verifies the token, requires a workspace and checks that the token names the signal's tenant, workspace
and actor. It raises the same `TokenError` and `Forbidden('workspace_required')`, and records the same `rejected`
decisions. It records nothing as `granted` or `denied`, because the permission is decided afterwards by the policy.

`EventRequest` accepts a `SignalEvent` as its event and a plain user id as its requestor, so a request that arrived as a
signal can be decided without reading the tenant, workspace and user. `request.requestor_id` is the id of whoever asked,
for a `User`, the `System` or an id.

## The rules

`decide(request, claims, *, permission, resource_tenant_id=None)` returns an `EventRequestResponse` holding one decision.
The first rule that applies decides:

1. The claims lack `permission`: denied, reason `insufficient_privileges`, not in effect.
2. `resource_tenant_id` is `None` (owned by the platform): approved, reason `access_permitted`, in effect.
3. The resource is in the caller's tenant and the caller is its owner: approved, reason `permitted`, in effect.
4. The resource is in the caller's tenant: approved, reason `access_permitted`, in effect.
5. The resource is in another tenant: approved conditionally, reason `approval_required`, not in effect until approved.

`access_permitted` means the caller's role grants access and no owner was involved; `permitted` stays for the owner
acting on their own resource. In rule 5 the decision carries one open condition, `approval_granted`, that expires at the
clock plus `approval_expiry`. A reply with that answer reason from the owner of the resource meets it.

## Settings

- `determined_by`: the id placed on every decision, normally the service id. Default: none.
- `approval_expiry`: how long an approval may stay open. Default: 5 days.
- `clock`: a function that returns the current time. Default: now, in UTC. Give a fixed one in tests.

The rule for another tenant (rule 5) is the owner's to refine; change only `DecisionPolicy`.
