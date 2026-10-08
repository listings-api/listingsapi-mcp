# Webhooks

Use webhooks instead of polling when the integration needs to know *when* something changed: a review arrived, a listing went live, a post was rejected, a publisher connection needs re-authorization. The webhook says when; the REST endpoint says what.

## The model

- **One URL per account, no per event subscription.** Every documented event is delivered to that one URL. Branch on the `event` field and return 200 for anything you do not recognize.
- Configured in the dashboard under Webhooks: save a URL, generate a signing secret, pass endpoint verification.
- Deliveries are signed. Header `X-ListingsAPI-Signature: sha256=<base64 HMAC-SHA256 of the raw body>`. Compare in constant time against the raw request bytes, not a re-serialized body. The digest is base64, not hex.
- **One attempt, 5 second timeout, no retries.** Return 2xx fast and do the work in a job. A 3xx counts as a failure.
- Plan entitlement and a per plan webhook rate limit apply. Over the limit, the event is dropped and recorded as `rate_limited`, not queued.

## Events (18)

| Family | Events | Pairs with |
| --- | --- | --- |
| `listing.submission` | 1 | `GET /locations/{id}/listings/premium` |
| `profile.*` | created, updated, deleted | Locations |
| `connection.*` | connected, disconnected, reauth, inaccessible, google_verification_verified, google_verification_failed | Connected accounts |
| `interaction.*` | review, response | Reviews |
| `local_post.*` | created, published, rejected, deleted | Posts |
| `review_analytics.*` | daily_snapshot, weekly_snapshot | Review analytics overview |

Two shapes to know: `listing.submission` is a legacy payload with no envelope (`status` of `success`, `incomplete` or `canceled`, `live_link`, `error_message`). `interaction.*` carries `location_id` as a numeric string or `null`; do not rely on its type.

## When to still poll

Verification progress emits nothing while in flight; poll `googleVerificationStatus` on the location during a verification. Analytics numbers are pull only. And webhooks confirm a change happened, not that your copy is complete: on `profile.updated`, re-read the location rather than trusting `changed_fields` alone.

Full reference: `https://listingsapi.com/docs/webhooks-overview`, `-signatures`, `-delivery`, `-events`.
