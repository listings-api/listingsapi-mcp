# Rate limits, retries and error handling

## Limits per plan

Limits are per account, not per key, across three windows. Every request costs one unit regardless of endpoint. A trial runs on the plan chosen at signup and has that plan's limits from the first call.

| Plan | Per minute | Per hour | Per day |
| --- | --- | --- | --- |
| Launch ($99 per month, 4 locations) | 10 | 600 | 7,200 |
| Growth ($499 per month, 25 locations) | 50 | 3,000 | 36,000 |
| Enterprise | Per contract | Per contract | Per contract |

Every metered response carries headers you can read before you hit the wall:

```
X-RateLimit-Minute-Limit / X-RateLimit-Minute-Remaining / X-RateLimit-Minute-Reset
X-RateLimit-Hour-Limit   / X-RateLimit-Hour-Remaining   / X-RateLimit-Hour-Reset
X-RateLimit-Day-Limit    / X-RateLimit-Day-Remaining    / X-RateLimit-Day-Reset
```

`Reset` values are unix seconds when the window flips. `X-RateLimit-Limit`, `-Remaining` and `-Reset` mirror the minute window.

## The 429

```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Request exceeded the minute limit. Retry after 30s.",
    "retry_after_seconds": 30,
    "limiting_window": "minute",
    "correlation_id": "9f2c1e64-2b1a-4b0e-9f1a-2c7d5e8a1b3c",
    "doc_url": "https://listingsapi.com/docs/error-codes#rate_limited"
  }
}
```

The `Retry-After` header carries the same number of seconds. Sleep for `retry_after_seconds`, then retry. If it is somehow absent, back off exponentially with jitter, capped at 30 seconds. Both official SDKs do this for you, two retries by default.

What causes 429s in practice:

- A loop that issues one request per location, in parallel or in a tight sequence, on a Launch plan. Ten locations is one minute of budget.
- Parallel pagination. Fetch pages one at a time.
- Polling a status endpoint every few seconds. Poll on a schedule measured in minutes.

Design rule for a sync job: a token bucket sized to the plan minus headroom, for example 8 per minute on Launch, shared by every worker in the process.

## Error envelopes

There are three shapes. Test for all of them: `errors` is an array, `error` is an object.

### Shape 1: request level, top level `errors[]`

The request failed before the operation ran. HTTP status matches the failure.

```json
{ "data": { "createLocation": null }, "errors": [{ "message": "SY90005: Invalid Token" }] }
```

| Status | Meaning | Typical code |
| --- | --- | --- |
| 400 | Bad shape: body not wrapped in `input`, unknown field, bad enum, unparseable filter, or a Read key on a write | `SY90006`, `SY90016` |
| 401 | Key missing, malformed or revoked | `SY90005` |
| 403 | Key valid but not permitted for this resource | `SY90003` |
| 404 | Path or resource id does not exist | `SY90002` |
| 502 | Upstream failure; safe to retry a read | `SY90007` |

### Shape 2: mutation validation, nested `data.<op>.errors[]` on HTTP 200

A well formed write reached the resolver and a business rule rejected it. The transport succeeded, so the status is 200.

```json
{
  "data": {
    "createLocation": {
      "success": false,
      "errors": [{ "message": "SY10126: City is Mandatory" }, { "message": "SY10005: Description ..." }],
      "location": null
    }
  }
}
```

The gateway also copies nested errors into the top level `errors` array, so a single check of `errors.length > 0` catches shapes 1 and 2 on the wire. Check both anyway. Do not rely on `success` alone: some mutations have it (`createLocation`, `createGmbListingForLocation`, `connectListing`), others do not (`respondToInteraction` returns `interaction` and `errors`). `errors` empty or `null` means success.

Codes in the `SY10xxx` range name a location field. `SY810xx` codes come from the connected accounts endpoints and arrive nested too.

### Shape 3: gateway level, a single `error` object

The gateway rejected the request before translating it. This is the only shape that carries `correlation_id`. Statuses: 429 (rate limit), 503 (rate limiter backend unavailable, retry), 500 (gateway catch all).

## `correlation_id`

Present on gateway level `error` objects (shape 3), not on `errors[]` arrays, and not as a response header. When it is present, log it with the request and quote it to `support@listingsapi.com`. For shape 1 and 2 failures, log the full `errors` array and the timestamp instead.

## Retry rules

- **Reads** (GET): retry on 429 after `retry_after_seconds`, and on 502 and 503 with exponential backoff, up to a small cap.
- **Writes** (POST): the API has no idempotency key. `clientMutationId` is echoed back but does not deduplicate. A write that timed out or returned 5xx may have committed. Before repeating a create, read back by a key you control: `GET /locations-by-store-codes` for a location, `GET /posts/{id}` for a post, the interaction's response list for a reply. Only repeat if it is absent.
- **401 and SY90016**: never retry. Fix the key.
- **Nested validation errors**: never retry. Fix the input.

## Handling errors in code

Order of checks for every response:

1. HTTP status. 429 goes to the retry path. 401 stops. 5xx goes to the read retry path or the write read back path.
2. Body `error` object present: gateway failure, log `correlation_id`.
3. Body `errors` array non empty: request or validation failure, log the messages, parse the leading `SYxxxxx` code.
4. On a write, `data.<op>.errors` non empty: validation failure even on 200.
5. `data.<op>` is `null` with nothing else: treat as failure.

Both SDKs collapse all of this into typed exceptions and raise on 200 bodies that carry errors. Python: `listingsapi.APIError` with `.status_code`, `.code`, `.errors`; `RateLimitError.retry_after`. Node: `APIError` with `.statusCode`, `.code`, `.errors`; `RateLimitError.retryAfter`.
