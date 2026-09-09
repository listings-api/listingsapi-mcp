# Authentication and access levels

## The header

Every REST request carries one header. The scheme is the literal word `API`, then a space, then the key.

```
Authorization: API <your-api-key>
```

Base URL: `https://listingsapi.com/api/v4`. There is no sandbox. Every call runs against the live account, and writes publish to real Google and Facebook profiles.

A missing, malformed or revoked key returns HTTP 401 with `SY90005: Invalid Token` in the top level `errors` array. Do not retry with the same key.

## Where keys come from

A person signs up at `https://listingsapi.com/signup`, and the first key is issued automatically. More keys are created at `https://listingsapi.com/dashboard/api-keys`. There is no programmatic way to create a key from outside the dashboard.

Each key has an access level chosen at creation:

| Level | Allows |
| --- | --- |
| Read | Every GET, every report, every list |
| Write | Everything Read allows, plus creating and updating locations, replying to reviews, publishing posts, connecting accounts |

A Read key that calls a write endpoint is rejected before the operation runs. The response carries `SY90016: Write operations not permitted for read-only API key` in the top level `errors` array. The gateway returns it as HTTP 400. Some documentation pages describe permission failures as 403, so match on the `SY` code rather than the status.

An account holds at most **5 active keys**. Creating a sixth fails with `SY90079`. Revoked keys do not count. This matters for integrations that mint a key per environment or per user: budget them.

All keys on an account share one rate limit budget. A second key does not double the limit.

## Which credential for which kind of app

| Situation | Credential |
| --- | --- |
| Your app works with one Listings API account (your own) | One API key, read from the environment |
| Your app is a product whose users each have their own Listings API account | One API key per user, created by that user in their own dashboard and entered into your app |
| Your app is an MCP client or agent host and the user should approve access on a consent screen | OAuth 2.0, against the MCP endpoint only |

### OAuth 2.0 is for the MCP endpoint, not for REST

The authorization server at `https://listingsapi.com` issues Bearer access tokens with scopes `read` and `write`. Those tokens are accepted by `https://listingsapi.com/mcp` and nowhere else. The REST gateway at `/api/v4` only understands the `API` scheme.

What happens under the hood: when a user approves the consent screen, the platform creates one API key on their account named after your client, and the Bearer token is a handle in front of that key. So OAuth does not give you a REST credential; it gives your MCP client a way to obtain one without the user copying it.

If you are building a REST integration that serves many accounts, plan for key collection:

1. Each customer creates a key in their dashboard (Read or Write to match what your app does) and pastes it into your app.
2. Store it encrypted at rest, keyed by tenant. Treat it like a password.
3. Send it per request as `Authorization: API <that-customer-key>`.
4. Handle 401 per tenant: the customer revoked the key. Do not retry, mark the tenant as disconnected and ask for a new key.
5. Remember the 5 key cap applies on the customer's account, not yours.

OAuth details, for MCP clients only: discovery at `https://listingsapi.com/.well-known/oauth-authorization-server`, dynamic client registration at `/oauth/register` (no initial token, no client secret, PKCE S256 required), authorize at `/oauth/authorize`, token at `/oauth/token`, revoke at `/oauth/revoke`. `scope` omitted grants `read`. The full agent guide is at `https://www.listingsapi.com/auth.md`.

## Rules for handling the key in code

- Read it from an environment variable. Both official SDKs read `LISTINGSAPI_KEY` by default, so use that name.
- Never put it in source, in a config file that is committed, in a client side bundle or in a URL.
- Log the first eight characters at most when debugging which key a request used.
- Rotation: create the new key, deploy it, then revoke the old one in the dashboard. Revocation is immediate.
