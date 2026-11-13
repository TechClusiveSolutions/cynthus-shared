# Identity Email Signals (`audit.identity.email.*`)

An account's email address is verified with the single-use link sent to it.

---

## `audit.identity.email.verified`

**Signal class:** `AuditIdentityEmailVerifiedSignal`
**Message class:** `IdentityEmailVerifiedMessage`
**Payload class:** `IdentityEmailVerifiedPayload`

**Emitted by:** `cynthus-auth`
**Consumed by:** `cynthus-audit`

**When:** A person uses the link in the verification email. From now on the account can sign in. Records the verification for `cynthus-audit` and lets other services react to a user who is ready to use the application. The payload never carries a password, a password hash or a token.

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
  - Description: The identifier of the user whose address was verified.
- `username`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The email address that was verified.

Set the envelope `lifecycle_action` to `updated`.
