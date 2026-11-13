# Identity Token Signals (`audit.identity.token.*`)

An access token is a signed JWT that proves who a caller is and what they may do.

---

## `audit.identity.token.issued`

**Signal class:** `AuditIdentityTokenIssuedSignal`
**Message class:** `IdentityTokenIssuedMessage`
**Payload class:** `IdentityTokenIssuedPayload`

**Emitted by:** `cynthus-auth`
**Consumed by:** `cynthus-audit`

**When:** An access token is issued. Records which token was issued to whom and with which permissions. The token itself is never included.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `user_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the user.
- `token_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the access token (its jti claim).
- `key_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the key that signed the token.
- `expires_in`
  - Type: `int`
  - Required: Yes
  - Default: none
  - Description: Seconds until the token expires.
- `roles`
  - Type: `List[str]`
  - Required: No
  - Default: empty list
  - Description: The roles carried by the token.
- `permissions`
  - Type: `List[str]`
  - Required: No
  - Default: empty list
  - Description: The permissions carried by the token.

Set the envelope `lifecycle_action` to `created`.
