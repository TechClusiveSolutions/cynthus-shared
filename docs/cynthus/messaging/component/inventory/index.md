# Inventory Domain Signals

The `inventory` domain covers storage locations, the shelves within them, and the items held on those shelves. All signals in this domain are published to `cynthus-events-topic` and carry the prefix `public.inventory.*`.

---

## Aggregates

- `list`
  - Signal prefix: `public.inventory.list.*`
  - Description: Request and reply for an inventory listing.
- `location`
  - Signal prefix: `public.inventory.location.*`
  - Description: A location is a named physical storage space such as a pantry, fridge or freezer.
- `shelf`
  - Signal prefix: `public.inventory.shelf.*`
  - Description: A shelf is a subdivision of a location that holds items and has owners.
- `item`
  - Signal prefix: `public.inventory.item.*`
  - Description: An item is a quantity of a product held on a shelf.
- `owner`
  - Signal prefix: `public.inventory.owner.*`
  - Description: An owner is a user who is responsible for a shelf.

Asking the Inventory service to create, get, list, update or delete these records is done with the request and response signals described in [request.md](request.md).

---

## Not yet covered

Shelf ownership and role signals (`audit.inventory.location.role_*`), `public.inventory.mutation.recorded`, low-stock and expiry signals, orders and receipt scans are defined in the signal catalog but have no classes in this package yet.
