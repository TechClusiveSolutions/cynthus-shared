# Identity Domain Signals

The `identity` domain covers registration, email verification, sign-in, access tokens and the access decisions services make with them. These are write-once compliance records, so they carry the `audit.identity.*` prefix (see the signal catalog, Security and Identity) and are consumed by `cynthus-audit`. They are published to `cynthus-events-topic`.

---

## Aggregates

| Aggregate | Signal prefix | Description |
|---|---|---|
| `user` | `audit.identity.user.*` | A user registers an account, and signs in with a username and password. |
| `email` | `audit.identity.email.*` | The email address of an account is verified with the link sent to it. |
| `token` | `audit.identity.token.*` | An access token is a signed JWT that proves who a caller is and what they may do. |
| `access` | `audit.identity.access.*` | An access decision is made each time a service checks a caller token against the permission a request needs. |

---

## Reading the access signals

| Outcome | Signal | HTTP status |
|---|---|---|
| The token is valid and grants the permission | `audit.identity.access.granted` | 2xx |
| No valid token (missing, malformed, expired, forged, or for another caller) | `audit.identity.access.rejected` | 401 |
| A valid token that lacks the permission (role-based access violation) | `audit.identity.access.denied` | 403 |

Unknown callers have no tenant, so a signal about them carries the nil UUID (`00000000-0000-0000-0000-000000000000`) as organization, workspace and actor.
