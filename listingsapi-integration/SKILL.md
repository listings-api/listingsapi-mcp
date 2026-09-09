---
name: listingsapi-integration
description: Use when a developer wants to integrate the Listings API (listingsapi.com) into code, whether building a new app on it or adding it to an existing app. Covers local listings, Google Business Profile, business locations, reviews and replies, posts, publisher analytics, the API key and OAuth credentials, the GraphQL shaped response envelope, cursor pagination, rate limits and the SDKs (listingsapi on PyPI, listingsapi-js on npm). Fires on phrases like "listings api", "listingsapi", "local listings", "google business profile api", "sync locations to google", "reply to reviews via api", "add listings api to my app".
---

# Listings API integration

The Listings API is a REST API at `https://listingsapi.com/api/v4`. You store a business location once and it is published to Google, Facebook, Bing, Apple Maps and 50 plus directories. The same API key reads and answers reviews, publishes posts and returns Google, Facebook and Bing performance data.

This skill is for writing code against that API. For exploring an account conversationally instead of writing code, point an MCP client at `https://listingsapi.com/mcp` with the same `Authorization: API <key>` header. That route is faster for questions like "which locations have no phone number". It is not a substitute for an integration.

## Step 1: ask one question, then stop

Before scaffolding, installing or editing anything, ask exactly this, in one message, with nothing else attached:

> Are you (1) building something new on top of the Listings API, or (2) adding the Listings API to an app that already exists? Reply 1 or 2.

Rules:

- If the opening request already answers it, do not ask. Say which path you inferred and why in one line, then continue. Infer path 2 only when the request names an existing app, codebase, service or repo ("add the Listings API to my app", "our backend", "this repo"). Infer path 1 only when it says build, new, from scratch, prototype, or names something that does not exist yet ("build a dashboard on the Listings API").
- Everything else is not obvious, so ask. A business having stores, branches or locations does not imply an existing app. "Integrate the Listings API for our 40 stores" could be either path. Ask.
- Never ask this question twice. Never bundle it with other questions.
- Do not run commands, create files or read the codebase until it is answered, except to infer the answer from the request itself.

## Path 1: new app

Establish three facts before writing code. Ask for the ones the request did not settle, in one message:

1. **Language and framework.** Ask, and do not suggest or assume one. After the answer: official SDKs exist for Python (`pip install listingsapi`, 3.9+) and Node (`npm install listingsapi-js`, 18+), so use one when it matches. Every other language calls REST directly with its usual HTTP client.
2. **One Listings API account or many.** This is the decision that is expensive to undo.
   - One account: one API key from the dashboard, read from an environment variable.
   - Many accounts (your users each have their own Listings API account): the REST API has no OAuth. Each customer creates a key in their own dashboard and gives it to your app. Store it encrypted, one per tenant, and send it as `Authorization: API <key>` on their requests. OAuth 2.0 Bearer tokens exist but are only accepted by the MCP endpoint, not by `/api/v4`. Read `references/authentication.md` before deciding.
3. **Write access at all.** If the app only reads, ask the person to create a Read key. A Read key that hits a write endpoint fails with `SY90016`.

Then scaffold, in this order, and have the person run each step before the next:

1. A small typed client module: base URL, `Authorization: API <key>` header, JSON in and out, 30 second timeout.
2. Config that reads the key from `LISTINGSAPI_KEY` in the environment. Never from source, never committed, never shipped to a browser.
3. A pagination helper that follows `pageInfo.endCursor` while `pageInfo.hasNextPage` is true and also stops on an empty `edges` array. Not every endpoint pages the same way; see `references/envelope-and-pagination.md`.
4. A rate limiter that stays under the plan's per minute limit and a retry path that sleeps for `retry_after_seconds` on a 429. Retry reads only. Writes have no idempotency key.
5. Error handling that reads the HTTP status, then the top level `errors[]`, then `data.<operation>.errors[]` on writes, and logs `correlation_id` when the body has one.
6. One read flow end to end, for example list locations and print name and city. Run it with a real key before adding anything else.

Runnable Python and TypeScript versions of steps 1 to 5 are in `references/client-scaffold.md`. Copy from there rather than writing from memory.

## Path 2: existing app

Read before proposing. Get these facts from the code, not from the person. The only thing to ask for is where the code is, if you cannot see it. Find out:

- Which language and framework the app is in. Read it from the code, never assume it from the request.
- How the app makes outbound HTTP calls (a shared client class, a wrapper around the platform's HTTP library) and reuse it.
- Where secrets and config live (an encrypted credentials store, environment files, a secrets manager, a settings module) and add `LISTINGSAPI_KEY` there.
- Whether there is a job queue or scheduler. Location sync and review polling belong in background jobs, not in request handlers.
- The testing setup, so the new client gets tests in the same style. Record real responses as fixtures; the envelope is easy to get wrong from memory.
- Whether the app already models stores, branches, venues or locations. Almost always yes, and that model is the anchor for the integration.

Then settle the mapping before writing the client:

1. **Record mapping.** One app record maps to one Listings API location. Store the returned base64 location `id` on your record. Also send your own primary key as `storeId`; it must be unique per account and lets you look records up later with `GET /locations-by-store-codes` without trusting your own stored id.
2. **Source of truth per field.** For each field (name, address, phone, hours, description, categories, website) decide whether your app or the Listings API wins. Usually your app owns identity and address, and the Listings API owns listing status and review data. Write the decision down in the code as a comment or a mapping table. Everything after this depends on it.
3. **Backfill separately from ongoing sync.** Backfill is a one time job over records that already exist, rate limited, resumable and idempotent by `storeId`. Ongoing sync is a hook on record changes that enqueues an update. Do not combine them into one loop.
4. **One location first.** Create one location for one record, confirm it appears in `GET /locations`, confirm the mapping round trips, then run the backfill.

Add the client in the app's own conventions. Do not introduce a new HTTP library, a new config system or a new job framework because the SDK examples use one.

## What every integration must get right

| Fact | Detail | Reference |
| --- | --- | --- |
| Auth header | `Authorization: API <key>`. Bearer tokens are for the MCP endpoint only | authentication.md |
| Keys | Read or Write access level, at most 5 active keys per account, all keys share one rate limit budget | authentication.md |
| Envelope | Reads: `data.<field>`. Cursor lists: `edges[].node` plus `pageInfo`. Offset lists: `records[]` plus `pageInfo`. Catalog endpoints: plain arrays | envelope-and-pagination.md |
| Writes | HTTP 200 with `data.<op>.errors` populated is a failure. Always read it | rate-limits-retries-errors.md |
| Rate limits | Launch 10 per minute, Growth 50, plus hourly and daily caps. 429 carries `retry_after_seconds` | rate-limits-retries-errors.md |
| Retries | Retry reads. Never blind retry a write; read back by `storeId` first | rate-limits-retries-errors.md |
| Location create | `name`, `description` of 200 plus characters, `countryIso`, `subCategoryId`, `city`. Add `street` and `phone` or it cannot publish | locations.md |
| IDs | Locations use a base64 Relay id, `base64("Location:1800289")`. Path parameters accept the number too, request bodies do not | envelope-and-pagination.md |
| Connected accounts | Review replies, posts and Google, Facebook and Bing analytics need the publisher account connected and matched to the location first | connected-accounts.md |
| GBP listing create | `{ "input": { "locationId", "connectedAccountId" } }`, asynchronous, `success: true` means accepted, not live | connected-accounts.md |

## References

Load only what the current step needs.

- `references/authentication.md`: API keys, access levels, the 5 key cap, why OAuth does not apply to REST, multi tenant key storage.
- `references/envelope-and-pagination.md`: the three response shapes, `pageInfo`, cursors, id encoding.
- `references/rate-limits-retries-errors.md`: limits per plan, the 429 body, the three error envelopes, `correlation_id`, safe retry rules.
- `references/client-scaffold.md`: runnable Python and TypeScript clients with pagination, rate limiting, retry and error surfacing. SDK usage for both languages.
- `references/locations.md`: the location model, required fields, hours, categories, update and archive, store codes.
- `references/connected-accounts.md`: connecting Google and Facebook, matching, connecting a listing, creating a GBP listing, checking listing status.
- `references/reviews.md`: listing reviews, filters, replying, editing, the response status flow.
- `references/posts.md`: announcements, events, offers, the `input` wrapper, publish status.
- `references/analytics.md`: Google, Facebook and Bing metrics, date ranges, what an empty response means.
- `references/webhooks.md`: when to use webhooks instead of polling, the one URL per account model.
- `references/troubleshooting.md`: symptom to cause table for the failures integrations hit first.
