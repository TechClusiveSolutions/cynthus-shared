# Identity Domain Signals

The `identity` domain covers registration, email verification, sign-in, access tokens and the access decisions services make with them. These are write-once compliance records, so they carry the `audit.identity.*` prefix (see the signal catalog, Security and Identity) and are consumed by `cynthus-audit`. They are published to `cynthus-events-topic`.

---

## Aggregates

- `user`
  - Signal prefix: `audit.identity.user.*`
  - Description: A user registers an account, and signs in with a username and password.
- `email`
  - Signal prefix: `audit.identity.email.*`
  - Description: The email address of an account is verified with the link sent to it.
- `token`
  - Signal prefix: `audit.identity.token.*`
  - Description: An access token is a signed JWT that proves who a caller is and what they may do.
- `access`
  - Signal prefix: `audit.identity.access.*`
  - Description: An access decision is made each time a service checks a caller token against the permission a request needs.

---

## Reading the access signals

- The token is valid and grants the permission
  - Signal: `audit.identity.access.granted`
  - HTTP status: 2xx
- No valid token (missing, malformed, expired, forged, or for another caller)
  - Signal: `audit.identity.access.rejected`
  - HTTP status: 401
- A valid token that lacks the permission (role-based access violation)
  - Signal: `audit.identity.access.denied`
  - HTTP status: 403

Unknown callers have no tenant, so a signal about them carries the nil UUID (`00000000-0000-0000-0000-000000000000`) as organization, workspace and actor.
