# Shopping List Domain Signals

The `shopping_list` domain covers shopping lists and the items on them. A list is a standing notebook of what a person or business wants; the items are the request. The requester can also check an item off after buying it in person. Orders placed with a store or marketplace, substitutions and the order planner come in a later phase and will add their own signals. All are `public.*` and are published to `cynthus-events-topic`.

The names repeat the aggregate (`list`, `item`) as the other domains do, so the signal for a new list is `public.shopping_list.list.created`.

---

## Signals

| Signal | Emitted by | Purpose |
|---|---|---|
| `public.shopping_list.list.created` | `cynthus-shopping` | Lets other services know a shopping list exists and whether it is the workspace procurement target. |
| `public.shopping_list.list.updated` | `cynthus-shopping` | Lets other services know which fields of a list changed, including archiving it. |
| `public.shopping_list.list.deleted` | `cynthus-shopping` | Lets other services know a list was removed; purchase history is kept under the retention policy. |
| `public.shopping_list.item.added` | `cynthus-shopping` | Lets other services know an item was added to a list, by hand or automatically. |
| `public.shopping_list.item.updated` | `cynthus-shopping` | Lets other services know which fields of a list item changed. |
| `public.shopping_list.item.checked_off` | `cynthus-shopping` | Lets other services know the requester bought the item in person; feeds the purchase history. |
| `public.shopping_list.item.removed` | `cynthus-shopping` | Lets other services know an item left the list without being bought. |

---

## `public.shopping_list.list.created`

**Signal class:** `PublicShoppingListListCreatedSignal`
**Message class:** `ShoppingListCreatedMessage`
**Payload class:** `ShoppingListCreatedPayload`

**Emitted by:** `cynthus-shopping`
**Consumed by:** `cynthus-audit`

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `schema_version` | `int` | No | `1` | Payload schema version. |
| `list_id` | `str` | Yes | — | The identifier of the shopping list. |
| `owner_id` | `str` | Yes | — | The identifier of the user who owns the list. |
| `name` | `str` | Yes | — | The name of the list. |
| `is_procurement_target` | `bool` | No | `False` | Whether the list receives items added automatically from low stock. |

---

## `public.shopping_list.list.updated`

**Signal class:** `PublicShoppingListListUpdatedSignal`
**Message class:** `ShoppingListUpdatedMessage`
**Payload class:** `ShoppingListUpdatedPayload`

**Emitted by:** `cynthus-shopping`
**Consumed by:** `cynthus-audit`

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `schema_version` | `int` | No | `1` | Payload schema version. |
| `list_id` | `str` | Yes | — | The identifier of the shopping list. |
| `owner_id` | `str` | Yes | — | The identifier of the user who owns the list. |
| `changed` | `List[str]` | No | `[]` | The fields that changed. |

---

## `public.shopping_list.list.deleted`

**Signal class:** `PublicShoppingListListDeletedSignal`
**Message class:** `ShoppingListDeletedMessage`
**Payload class:** `ShoppingListDeletedPayload`

**Emitted by:** `cynthus-shopping`
**Consumed by:** `cynthus-audit`

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `schema_version` | `int` | No | `1` | Payload schema version. |
| `list_id` | `str` | Yes | — | The identifier of the shopping list. |
| `owner_id` | `str` | Yes | — | The identifier of the user who owns the list. |

---

## `public.shopping_list.item.added`

**Signal class:** `PublicShoppingListItemAddedSignal`
**Message class:** `ShoppingListItemAddedMessage`
**Payload class:** `ShoppingListItemAddedPayload`

**Emitted by:** `cynthus-shopping`
**Consumed by:** `cynthus-analysis`, `cynthus-audit`

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `schema_version` | `int` | No | `1` | Payload schema version. |
| `list_id` | `str` | Yes | — | The identifier of the shopping list. |
| `item_id` | `str` | Yes | — | The identifier of the list item. |
| `name` | `str` | Yes | — | What the item or list is called. |
| `quantity` | `Optional[float]` | No | `None` | How much was asked for. |
| `unit` | `Optional[str]` | No | `None` | The unit code of the quantity. |
| `notes` | `Optional[str]` | No | `None` | The requester notes for the item. |
| `source` | `str` | No | `'manual'` | How the item got on the list: manual, low_stock, generated or meal_gap. |
| `catalog_item_id` | `Optional[str]` | No | `None` | The catalog product the item refers to. |
| `inventory_item_id` | `Optional[str]` | No | `None` | The inventory item that ran low, when the item came from low stock. |

---

## `public.shopping_list.item.updated`

**Signal class:** `PublicShoppingListItemUpdatedSignal`
**Message class:** `ShoppingListItemUpdatedMessage`
**Payload class:** `ShoppingListItemUpdatedPayload`

**Emitted by:** `cynthus-shopping`
**Consumed by:** `cynthus-analysis`, `cynthus-audit`

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `schema_version` | `int` | No | `1` | Payload schema version. |
| `list_id` | `str` | Yes | — | The identifier of the shopping list. |
| `item_id` | `str` | Yes | — | The identifier of the list item. |
| `changed` | `List[str]` | No | `[]` | The fields that changed. |

---

## `public.shopping_list.item.checked_off`

**Signal class:** `PublicShoppingListItemCheckedOffSignal`
**Message class:** `ShoppingListItemCheckedOffMessage`
**Payload class:** `ShoppingListItemCheckedOffPayload`

**Emitted by:** `cynthus-shopping`
**Consumed by:** `cynthus-analysis`, `cynthus-audit`

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `schema_version` | `int` | No | `1` | Payload schema version. |
| `list_id` | `str` | Yes | — | The identifier of the shopping list. |
| `item_id` | `str` | Yes | — | The identifier of the list item. |
| `name` | `str` | Yes | — | What the item or list is called. |
| `quantity_purchased` | `Optional[float]` | No | `None` | How much was actually bought. |
| `unit` | `Optional[str]` | No | `None` | The unit code of the quantity bought. |
| `provider_id` | `Optional[str]` | No | `None` | The store or vendor it was bought from. |

---

## `public.shopping_list.item.removed`

**Signal class:** `PublicShoppingListItemRemovedSignal`
**Message class:** `ShoppingListItemRemovedMessage`
**Payload class:** `ShoppingListItemRemovedPayload`

**Emitted by:** `cynthus-shopping`
**Consumed by:** `cynthus-audit`

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `schema_version` | `int` | No | `1` | Payload schema version. |
| `list_id` | `str` | Yes | — | The identifier of the shopping list. |
| `item_id` | `str` | Yes | — | The identifier of the list item. |
