---
name: listingsapi-integration
description: Help developers and ListingsAPI customers integrate the Listings API into a new or existing application, from secure authentication and a first API read through location setup, publisher connections, submissions, and status checks. Use for REST or SDK integration code and customer onboarding; routine account operations can use an existing MCP connection.
license: MIT
---

# ListingsAPI integration

Build a working integration around the user's language, existing application, and intended publisher workflow. The REST base URL is `https://listingsapi.com/api/v4`. The hosted MCP endpoint is `https://listingsapi.com/mcp`.

## Choose the path from the request

Infer whether the user is adding to an existing app, building a new one, or onboarding a ListingsAPI account. Inspect an available codebase to learn its language, HTTP client, configuration, job queue, and testing conventions. Reuse them. Ask for missing decisions only when they affect the next step; do not repeat questions the user already answered.

For a new app, establish the language/framework and whether it serves one ListingsAPI account or multiple customer accounts. For account onboarding without a new app, use existing MCP tools where available and provide a small REST or SDK example only when it helps. Do not scaffold an application merely to connect a publisher.

Read [the first-location walkthrough](references/onboarding.md) for authentication, location creation, publisher linking, and submission checks. It builds on the [client scaffold](references/client-scaffold.md), which supplies Python and TypeScript examples. These are examples to adapt and validate, not a reason to replace the application's existing libraries.

## Authenticate and make one read

- REST requests use `Authorization: API <key>`. MCP client OAuth bearer tokens do not authenticate REST. Prefer the existing MCP client's OAuth flow when that is the chosen integration route.
- Keep API keys server-side in an environment variable such as `LISTINGSAPI_KEY` or the app's secret store. Never request a secret in chat, commit it, return it to a browser, or log the authorization header.
- Use a Read key for reads. Location writes and publisher connections need Write access. Creating credentials or granting OAuth access requires the user's authorization; a skill installation does neither.
- For multiple customers, store each customer's key encrypted and bind every request/job to the correct tenant. Never reuse one tenant's cached client for another.
- Read a small location page first and handle an empty account as a valid result. Only run an authenticated read when access to that account is authorized. A Day Pass covers sandbox locations/listings, not reviews, posts, analytics, or connected publishers.

See [authentication](references/authentication.md) for the details. Check current endpoint and SDK contracts through `search_docs`, `get_doc`, and `get_endpoint` when available, or the official docs. Do not assume a REST route has an MCP tool. MCP exposes typed named arguments and may wrap them under `input` on the wire; use the runtime's schema.

## Map and set up one location

For an existing application, establish field ownership before syncing. Map one internal store record to one returned location Relay `id`, and use a unique `storeId` as a recovery lookup. Separate a resumable backfill from ongoing change jobs. A `storeId` lookup helps avoid duplicates but does not make concurrent creates idempotent; serialize work per store.

Gather verified name, description of at least 200 characters, address, country/state, phone, website, and category. Resolve taxonomy IDs from current lookup results, not example constants. Preserve full regular hours when changing special hours. Read [locations](references/locations.md) before creating or updating.

Before a consequential write, show the exact location, profile changes, and intended publisher scope. Obtain explicit approval for that concrete action; existing approval is sufficient when it covers the same values. A request to generate code or prepare an integration does not authorize running it against production. Never create a fake sample business in production to test an example.

Create or update only the approved record first, then read it back and verify the mapping. Creating a location queues listings for its configured plan publishers; it does not establish that every listing is live. Use `enabledSiteIds` from current plan-site results when the user approves a subset. Do not invent a separate submit-all endpoint.

## Connect publishers and verify outcomes

Read [connected accounts](references/connected-accounts.md) before connecting Google or Facebook, importing an existing listing, or creating a Google Business Profile. Prefer linking the correct existing listing when one exists. The user completes OAuth and publisher verification; never consent or claim verification on their behalf.

Matching produces suggestions. `MATCH_COMPLETED` is not proof that listings are linked. Show exact matches for approval, then confirm them or link a selected listing. A request to connect one profile does not authorize every suggested match.

Read premium listing status and the returned live URLs after submission. Pending verification, `IN_PROGRESS`, and `PENDING_APPROVAL` remain pending. `success: true` on Google listing creation means accepted; it does not prove the profile exists publicly. Return the confirmed state and a next step instead of promising a publication date.

## Make the integration reliable

Read [envelopes and pagination](references/envelope-and-pagination.md) and [errors and retries](references/rate-limits-retries-errors.md) before writing loops or jobs.

- Check HTTP failures, top-level `error`/`errors`, and nested mutation errors. Also check explicit `success: false` and the operation's expected result; HTTP 200 alone is insufficient.
- Preserve null analytics as unavailable data. Do not turn a null operation into an empty successful result.
- Follow each endpoint's actual cursor, offset, or array shape. Repeated/missing cursors, inconsistent pages, or interrupted reads must produce a partial-result warning instead of an apparently complete export.
- Share rate-limit budgets across workers for the same account. Honor server delays and bound read retries. Do not blindly retry a write: read back by the known record or business key and stop if its outcome remains ambiguous. `clientMutationId` is not an idempotency key.
- Log sanitized error codes, timestamps, and correlation IDs when present. Test against synthetic or sanitized fixtures; do not commit live customer responses as fixtures.

Validate generated code without live writes first. If a live test was requested, show the concrete action before executing it, then report accepted, pending, confirmed, and failed outcomes separately. Bulk work starts only after the one-record flow and the bulk scope are approved.

## Workflow references

Load only the reference needed for the task:

- [First-location walkthrough](references/onboarding.md): concrete read, create, connect, and status examples.
- [Authentication](references/authentication.md): keys, access levels, and tenant isolation.
- [Client scaffold](references/client-scaffold.md): Python/TypeScript transport, retries, and pagination.
- [Locations](references/locations.md): profile requirements, field mapping, hours, and updates.
- [Connected accounts](references/connected-accounts.md): OAuth, matches, existing listings, and Google creation.
- [Response envelope](references/envelope-and-pagination.md) and [error handling](references/rate-limits-retries-errors.md).
- [Reviews](references/reviews.md), [posts](references/posts.md), and [analytics](references/analytics.md): feature-specific contracts.
- [Webhooks](references/webhooks.md): event delivery for an application that needs it.
- [Troubleshooting](references/troubleshooting.md): common failure diagnosis.
