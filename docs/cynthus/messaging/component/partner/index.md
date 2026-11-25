# Partner Domain Signals

The `partner` domain covers the services that partners offer. All signals in this domain are published to `cynthus-events-topic` and carry the prefix `public.partner.*`.

---

## Aggregates

- `service_list`
  - Signal prefix: `public.partner.service_list.*`
  - Description: Request and reply for the list of services offered by partners. See [service_list.md](service_list.md).
