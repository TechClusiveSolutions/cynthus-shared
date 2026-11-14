# Identity Access Signals (`audit.identity.access.*`)

An access decision is made each time a service checks a caller token against the permission a request needs.

---

## `audit.identity.access.granted`

**Signal class:** `AuditIdentityAccessGrantedSignal`
**Message class:** `IdentityAccessGrantedMessage`
**Payload class:** `IdentityAccessGrantedPayload`

**Emitted by:** the service that checked the request
**Consumed by:** `cynthus-audit`

**When:** A request is let through. Records who used which permission on which resource.

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
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: The identifier of the access token (its jti claim), when it had one.
- `permission`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The permission the request needed.
- `resource`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The path of the resource that was requested.
- `method`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The HTTP method of the request.

Set the envelope `lifecycle_action` to `created`.

---

## `audit.identity.access.rejected`

**Signal class:** `AuditIdentityAccessRejectedSignal`
**Message class:** `IdentityAccessRejectedMessage`
**Payload class:** `IdentityAccessRejectedPayload`

**Emitted by:** the service that checked the request
**Consumed by:** `cynthus-audit`

**When:** A request has no valid token (missing, malformed, expired, forged or for another caller). Authentication failure (HTTP 401). Lets `cynthus-audit` and security monitoring see attempts without a valid identity.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `reason`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: Why the token was not accepted.
- `resource`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The path of the resource that was requested.
- `method`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The HTTP method of the request.

Set the envelope `lifecycle_action` to `created`.

---

## `audit.identity.access.denied`

**Signal class:** `AuditIdentityAccessDeniedSignal`
**Message class:** `IdentityAccessDeniedMessage`
**Payload class:** `IdentityAccessDeniedPayload`

**Emitted by:** the service that checked the request
**Consumed by:** `cynthus-audit`

**When:** A request has a valid token that does not grant the permission it needs. Authorization failure (HTTP 403), the role-based access violation. Lets `cynthus-audit` and security monitoring see users reaching beyond their role.

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
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: The identifier of the access token (its jti claim), when it had one.
- `required_permission`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The permission the request needed.
- `granted_permissions`
  - Type: `List[str]`
  - Required: No
  - Default: empty list
  - Description: The permissions the token carried.
- `roles`
  - Type: `List[str]`
  - Required: No
  - Default: empty list
  - Description: The roles the token carried.
- `resource`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The path of the resource that was requested.
- `method`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The HTTP method of the request.

Set the envelope `lifecycle_action` to `created`.
