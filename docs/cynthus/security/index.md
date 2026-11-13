# Access Token Security (`cynthus.security`)

Services trust the signed access token only (engineering standards, section 4). This package issues those tokens and verifies them, so every service checks them the same way.

---

## Classes

- `TokenIssuer`
  - Used by: `cynthus-auth`
  - Purpose: Signs access tokens with an RSA private key (RS256) and publishes the public key as a JWKS.
- `TokenVerifier`
  - Used by: API, Inventory and other services
  - Purpose: Fetches the JWKS and checks the signature, issuer, audience and expiry of a token.
- `TokenClaims`
  - Used by: all
  - Purpose: The verified identity: user, `organization_id`, `workspace_id`, token id, roles and permissions.
- `IssuedToken`
  - Used by: `cynthus-auth`
  - Purpose: What `TokenIssuer.issue_token` returns: the signed token plus its id, key id and lifetime.
- `RequirePermission`
  - Used by: services with HTTP routes
  - Purpose: FastAPI dependency: `Depends(RequirePermission('inventory:read'))` verifies the bearer token and the permission.
- `AccessDenied`
  - Used by: services with HTTP routes
  - Purpose: 401 or 403 error; register `access_denied_handler` to answer `{"error": ...}`.
- `AccessRecorder`
  - Used by: services that audit access
  - Purpose: Hook told about every granted, rejected and denied decision. Does nothing until a service subclasses it.
- `SignalAccessRecorder`
  - Used by: API and Inventory services
  - Purpose: An `AccessRecorder` that publishes `audit.identity.access.granted`, `.rejected` and `.denied` through a `SignalPublisher`.
- `BearerToken`
  - Used by: services that read HTTP headers or message properties
  - Purpose: Extracts the token from an `Authorization: Bearer <token>` value.
- `TokenError`
  - Used by: all
  - Purpose: Raised for any token that is missing, malformed, expired or not trusted. Carries a short `reason`.

---

## Token contents

- `iss`: Issuer. Defaults to `cynthus-auth`.
- `aud`: Audience. Defaults to `cynthus`.
- `sub`: The user's id.
- `jti`: The token's own id. Audit signals use it to name a token without recording the token.
- `iat`, `exp`: Issue and expiry times, in seconds since the epoch.
- `organization_id`, `workspace_id`: The tenant the token is valid for. Required.
- `roles`: Roles granted to the user, for example `workspace_administrator`.
- `permissions`: What the token may do, for example `inventory:read` and `inventory:write`.

A token that lacks `exp`, `iat`, `sub`, `iss`, `aud`, `organization_id` or `workspace_id` is rejected. Only RS256 is accepted, so an unsigned token or one signed with a shared secret never verifies.

---

## Verifier settings

`TokenVerifier.from_environment()` reads these variables:

- `AUTH_JWKS_URL`: `http://auth:8000/.well-known/jwks.json`
- `AUTH_ISSUER`: `cynthus-auth`
- `AUTH_AUDIENCE`: `cynthus`

The keys are cached and fetched again when a token names a key id that is not cached, so a key rotation needs no restart.

---

## Example

```python
verifier = TokenVerifier.from_environment()

try:
    claims = await verifier.verify(BearerToken.extract(request.headers.get('authorization')))
except TokenError as error:
    ...  # respond 401 with {"error": error.reason}

if not claims.has_permission('inventory:read'):
    ...  # respond 403
```

---

## Enforcing a permission on a route

```python
application.state.token_verifier = TokenVerifier.from_environment()
application.state.access_recorder = MyRecorder()  # optional, subclass of AccessRecorder
application.add_exception_handler(AccessDenied, access_denied_handler)


@router.get('/things')
async def list_things(claims: TokenClaims = Depends(RequirePermission('things:read'))):
    ...
```

A request with no valid token gets `401 {"error": "<reason>"}` and the recorder's `rejected` is called. A valid token without the permission gets `403` and the recorder's `denied` is called, which is the role-based access violation. A recorder that raises is logged and never changes the response.

For a websocket, call `RequirePermission(...).authorize(app, token, resource, 'WEBSOCKET')` and close the socket on `AccessDenied`.

---

## Publishing signals

`cynthus.messaging.publisher.SignalPublisher` publishes a `SignalMessage` to the events topic. `SignalPublisher.from_environment()` uses `SERVICE_BUS_CONNECTION_STRING` (the emulator) or else `SERVICE_BUS_NAMESPACE`. A caller token passed as `access_token` travels as the `authorization` message property, never in the body.
