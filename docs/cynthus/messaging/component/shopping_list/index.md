# Shopping List Domain Signals

The `shopping_list` domain covers shopping lists and the items on them. A list is a standing notebook of what a person or business wants; the items are the request. The requester can also check an item off after buying it in person. Orders placed with a store or marketplace, substitutions and the order planner come in a later phase and will add their own signals. All are `public.*` and are published to `cynthus-events-topic`.

A caller asks for list work with a request signal and gets the answer back as a response signal, so it is acknowledged at once; a change is then followed by the facts below. Item work is part of the list aggregate, so it uses the same pair.

The names repeat the aggregate (`list`, `item`) as the other domains do, so the signal for a new list is `public.shopping_list.list.created`.

---

## Signals

- `public.shopping_list.list.created`
  - Emitted by: `cynthus-shopping`
  - Purpose: Lets other services know a shopping list exists and whether it is the workspace procurement target.
- `public.shopping_list.list.updated`
  - Emitted by: `cynthus-shopping`
  - Purpose: Lets other services know which fields of a list changed, including archiving it.
- `public.shopping_list.list.deleted`
  - Emitted by: `cynthus-shopping`
  - Purpose: Lets other services know a list was removed; purchase history is kept under the retention policy.
- `public.shopping_list.item.added`
  - Emitted by: `cynthus-shopping`
  - Purpose: Lets other services know an item was added to a list, by hand or automatically.
- `public.shopping_list.item.updated`
  - Emitted by: `cynthus-shopping`
  - Purpose: Lets other services know which fields of a list item changed.
- `public.shopping_list.item.checked_off`
  - Emitted by: `cynthus-shopping`
  - Purpose: Lets other services know the requester bought the item in person; feeds the purchase history.
- `public.shopping_list.item.removed`
  - Emitted by: `cynthus-shopping`
  - Purpose: Lets other services know an item left the list without being bought.
- `public.shopping_list.list.requested`
  - Emitted by: `cynthus-core-api`
  - Purpose: Hands a request about lists or their items to the Shopping service so the caller gets an immediate acknowledgement.
- `public.shopping_list.list.responded`
  - Emitted by: `cynthus-shopping`
  - Purpose: Carries the outcome back to `cynthus-core-api`, which relays it to the caller.

---

## `public.shopping_list.list.created`

**Signal class:** `PublicShoppingListListCreatedSignal`
**Message class:** `ShoppingListCreatedMessage`
**Payload class:** `ShoppingListCreatedPayload`

**Emitted by:** `cynthus-shopping`
**Consumed by:** `cynthus-audit`

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `list_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the shopping list.
- `owner_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the user who owns the list.
- `name`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The name of the list.
- `is_procurement_target`
  - Type: `bool`
  - Required: No
  - Default: `False`
  - Description: Whether the list receives items added automatically from low stock.

---

## `public.shopping_list.list.updated`

**Signal class:** `PublicShoppingListListUpdatedSignal`
**Message class:** `ShoppingListUpdatedMessage`
**Payload class:** `ShoppingListUpdatedPayload`

**Emitted by:** `cynthus-shopping`
**Consumed by:** `cynthus-audit`

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `list_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the shopping list.
- `owner_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the user who owns the list.
- `changed`
  - Type: `List[str]`
  - Required: No
  - Default: `[]`
  - Description: The fields that changed.

---

## `public.shopping_list.list.deleted`

**Signal class:** `PublicShoppingListListDeletedSignal`
**Message class:** `ShoppingListDeletedMessage`
**Payload class:** `ShoppingListDeletedPayload`

**Emitted by:** `cynthus-shopping`
**Consumed by:** `cynthus-audit`

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `list_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the shopping list.
- `owner_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the user who owns the list.

---

## `public.shopping_list.item.added`

**Signal class:** `PublicShoppingListItemAddedSignal`
**Message class:** `ShoppingListItemAddedMessage`
**Payload class:** `ShoppingListItemAddedPayload`

**Emitted by:** `cynthus-shopping`
**Consumed by:** `cynthus-analysis`, `cynthus-audit`

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `list_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the shopping list.
- `item_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the list item.
- `name`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: What the item or list is called.
- `quantity`
  - Type: `Optional[float]`
  - Required: No
  - Default: `None`
  - Description: How much was asked for.
- `unit`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: The unit code of the quantity.
- `notes`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: The requester notes for the item.
- `source`
  - Type: `str`
  - Required: No
  - Default: `'manual'`
  - Description: How the item got on the list: manual, low_stock, generated or meal_gap.
- `catalog_item_id`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: The catalog product the item refers to.
- `inventory_item_id`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: The inventory item that ran low, when the item came from low stock.

---

## `public.shopping_list.item.updated`

**Signal class:** `PublicShoppingListItemUpdatedSignal`
**Message class:** `ShoppingListItemUpdatedMessage`
**Payload class:** `ShoppingListItemUpdatedPayload`

**Emitted by:** `cynthus-shopping`
**Consumed by:** `cynthus-analysis`, `cynthus-audit`

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `list_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the shopping list.
- `item_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the list item.
- `changed`
  - Type: `List[str]`
  - Required: No
  - Default: `[]`
  - Description: The fields that changed.

---

## `public.shopping_list.item.checked_off`

**Signal class:** `PublicShoppingListItemCheckedOffSignal`
**Message class:** `ShoppingListItemCheckedOffMessage`
**Payload class:** `ShoppingListItemCheckedOffPayload`

**Emitted by:** `cynthus-shopping`
**Consumed by:** `cynthus-analysis`, `cynthus-audit`

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `list_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the shopping list.
- `item_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the list item.
- `name`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: What the item or list is called.
- `quantity_purchased`
  - Type: `Optional[float]`
  - Required: No
  - Default: `None`
  - Description: How much was actually bought.
- `unit`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: The unit code of the quantity bought.
- `provider_id`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: The store or vendor it was bought from.

---

## `public.shopping_list.item.removed`

**Signal class:** `PublicShoppingListItemRemovedSignal`
**Message class:** `ShoppingListItemRemovedMessage`
**Payload class:** `ShoppingListItemRemovedPayload`

**Emitted by:** `cynthus-shopping`
**Consumed by:** `cynthus-audit`

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `list_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the shopping list.
- `item_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the list item.

---

## `public.shopping_list.list.requested`

**Signal class:** `PublicShoppingListListRequestedSignal`
**Message class:** `ShoppingListRequestedMessage`
**Payload class:** `ShoppingListRequestedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-shopping`

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `operation`
  - Type: `Literal['create', 'get', 'list', 'update', 'delete', 'add_item', 'update_item', 'remove_item', 'check_off_item']`
  - Required: Yes
  - Default: none
  - Description: What to do with shopping lists or their items.
- `resource_id`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: The list to get, change or delete, or the list an item belongs to.
- `item_id`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: The item to change, remove or check off.
- `filters`
  - Type: `Dict[str, Any]`
  - Required: No
  - Default: `{}`
  - Description: Narrows a list of lists, for example `q`, `owner`, `archived`, `limit` or `offset`.
- `data`
  - Type: `Dict[str, Any]`
  - Required: No
  - Default: `{}`
  - Description: The fields to create or change a list or an item with.

`get` and `list` need `shopping:read`; every other operation needs `shopping:write`.

---

## `public.shopping_list.list.responded`

**Signal class:** `PublicShoppingListListRespondedSignal`
**Message class:** `ShoppingListRespondedMessage`
**Payload class:** `ShoppingListRespondedPayload`

**Emitted by:** `cynthus-shopping`
**Consumed by:** `cynthus-core-api`

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `operation`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The operation that was requested.
- `status`
  - Type: `int`
  - Required: Yes
  - Default: none
  - Description: `200`, `201` or `204` when it worked; `401`, `403`, `404`, `405`, `409`, `422` or `503` when it did not.
- `result`
  - Type: `Optional[Any]`
  - Required: No
  - Default: `None`
  - Description: The list, or the lists, when it worked.
- `error`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: Why the request failed.
