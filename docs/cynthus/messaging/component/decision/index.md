# Decision Domain Signals

The `decision` domain publishes every decision made on an event request (ADR-013) as its own signal, so the audit
engine and any other subscriber see decisions as they happen. A decision is not stored per service; the signal is the
record. All signals in this domain are published to `cynthus-events-topic` and carry the prefix `public.decision.*`.

---

## Aggregates

- `event_request`
  - Signal prefix: `public.decision.event_request.*`
  - Description: One signal for each answer to an event request.
  - Signals, with their classes:
    - `public.decision.event_request.approved`: `PublicDecisionEventRequestApprovedSignal`
    - `public.decision.event_request.approved_conditionally`: `PublicDecisionEventRequestApprovedConditionallySignal`
    - `public.decision.event_request.denied`: `PublicDecisionEventRequestDeniedSignal`
    - `public.decision.event_request.denied_conditionally`: `PublicDecisionEventRequestDeniedConditionallySignal`
  - Bases: `PublicDecisionSignalBase` (domain) and `PublicDecisionEventRequestSignalBase` (aggregate).

## Messages and payload

The four messages are `DecisionEventRequestApprovedMessage`, `DecisionEventRequestApprovedConditionallyMessage`,
`DecisionEventRequestDeniedMessage` and `DecisionEventRequestDeniedConditionallyMessage`. Each has its own `event_type`
(the signal name) and the same payload, `EventRequestDecisionPayload`:

- `schema_version`: `int`, at least `1`, default `1`
- `event_request_id`: `UUID`, the request that was decided
- `in_reply_to`: `UUID`, default `None`, the request the decided request answers
- `requested_event_type`: `str`, the event type of the request, for example `partner_service_list_requested`
- `requested_action`: `str`, the action the request asked for
- `requestor_id`: `UUID`, the user or system that made the request
- `answer`: `str`, one of `approved`, `approved_conditionally`, `denied`, `denied_conditionally`
- `answer_reason`: `str`, why the answer is what it is, for example `approval_required`
- `conditions`: list of `EventRequestDecisionConditionPayload`, default empty
  - `condition`: `str`, the answer reason a reply must carry to meet it
  - `status`: `str`, `open`, `satisfied`, `failed`, `waived` or `expired`
  - `expires_at`: `datetime`, default `None`
- `determined_by`: `UUID`, default `None`, the service that made the decision
- `determined_on`: `datetime`, when the decision was made

## Events and generator

- [events.md](events.md): the decision events and `EventRequestDecisionEvent.deciding`.
- [generator.md](generator.md): `DecisionSignalGenerator`, which turns the events into signal messages.
