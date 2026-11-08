# Identity User Signals (`audit.identity.user.*`)

A user registers an account, and signs in with a username and password.

---

## `audit.identity.user.authenticated`

**Signal class:** `AuditIdentityUserAuthenticatedSignal`
**Message class:** `IdentityUserAuthenticatedMessage`
**Payload class:** `IdentityUserAuthenticatedPayload`

**Emitted by:** `cynthus-auth`
**Consumed by:** `cynthus-audit`

**When:** A user signs in with correct credentials. Records the sign-in for `cynthus-audit`.

### Payload fields

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `schema_version` | `int` | No | `1` | Payload schema version. |
| `user_id` | `str` | Yes | — | The identifier of the user. |
| `username` | `str` | Yes | — | The username that was presented. |
| `method` | `str` | No | `'password'` | How the user proved who they are. |

Set the envelope `lifecycle_action` to `created`.

---

## `audit.identity.user.registered`

**Signal class:** `AuditIdentityUserRegisteredSignal`
**Message class:** `IdentityUserRegisteredMessage`
**Payload class:** `IdentityUserRegisteredPayload`

**Emitted by:** `cynthus-auth`
**Consumed by:** `cynthus-audit`

**When:** A person creates an account. The account cannot sign in until the address is verified (see `audit.identity.email.verified`). Records the registration for `cynthus-audit` and lets other services prepare for a new user. The payload never carries a password, a password hash or a token.

### Payload fields

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `schema_version` | `int` | No | `1` | Payload schema version. |
| `user_id` | `str` | Yes | — | The identifier of the new user. |
| `username` | `str` | Yes | — | The email address the account was registered with. |

Set the envelope `lifecycle_action` to `created`.

---

## `audit.identity.user.rejected`

**Signal class:** `AuditIdentityUserRejectedSignal`
**Message class:** `IdentityUserRejectedMessage`
**Payload class:** `IdentityUserRejectedPayload`

**Emitted by:** `cynthus-auth`
**Consumed by:** `cynthus-audit`

**When:** A sign-in is refused. Lets `cynthus-audit` and security monitoring see failed sign-ins. The password is never included.

### Payload fields

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `schema_version` | `int` | No | `1` | Payload schema version. |
| `username` | `str` | Yes | — | The username that was presented. |
| `reason` | `str` | No | `'invalid_credentials'` | Why the sign-in was refused. |

Set the envelope `lifecycle_action` to `created`.
