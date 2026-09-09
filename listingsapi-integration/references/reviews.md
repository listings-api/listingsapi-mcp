# Reviews and replies

Reviews are "interactions". An interaction's `id` is a plain UUID, not a base64 id.

## List reviews for a location

`GET /locations/{locationId}/reviews` is a cursor page under `data.interactions`. Default page is 20 and the endpoint never returns the whole history in one call.

Filters, all as query parameters, arrays JSON encoded:

| Parameter | Example | Note |
| --- | --- | --- |
| `startDate`, `endDate` | `2026-08-01` | Date range |
| `ratingFilters` | `[1,2]` | Star ratings to include |
| `responseStatus` | `["PENDING"]` | `PENDING` or `RESPONDED` |
| `siteUrls` | `["maps.google.com"]` | Publisher hosts |
| `sortOrder` | `["NEWEST_FIRST"]` | Or `OLDEST_FIRST`, `LAST_RESPONDED` |
| `searchString` | `parking` | Full text |
| `first`, `after` | | Cursor paging |

Node fields worth using: `id`, `source`, `content`, `authorName`, `rating`, `date`, `responded`, `responseCount`, `canRespond`, `permalink`. `totalCount` sits beside `pageInfo`.

Account wide: `GET /rollup_interactions` rolls review counts up across the account, for finding stores with the most unanswered reviews without a call per location.

## Reply

```
POST /locations/reviews/respond
{ "interactionId": "9e26d2a8-...", "responseContent": "Thank you for visiting. We are glad you enjoyed it." }
```

Not wrapped in `input`. Requires a Write key and the publisher account connected and matched to the location (see `connected-accounts.md`). Check `canRespond` on the interaction first; not every source accepts owner replies.

Response: `data.respondToInteraction.interaction` with `interactionStatus: CREATED`, and `errors`. There is no `success` field on this mutation; `errors` empty or `null` is success.

Posting is asynchronous. `CREATED` moves to `COMPLETED` or `CONFIRMED` when the publisher accepts it, or `FAILED`. Re-fetch with `GET /reviewDetails` before telling a user the reply is live. A reply that stays `CREATED` for a long time usually means the publisher connection is stale (`connectivityIssue` on the connected account).

Google accepts one owner reply per review. A second `respond` fails with `SY50121`. Use `POST /locations/reviews/respond/edit` to change an existing reply and `POST /locations/reviews/respond/archive` to remove it.

## Review analytics

`GET /locations/{locationId}/review-analytics-overview?startDate=&endDate=` returns KPIs under `data.interactionsAnalyticsStats.stats`: `total-reviews`, `new-reviews`, `overall-rating`, `review-response-rate`, each with `value` and `delta`. Sibling routes give a timeline and a per site breakdown.

## Design notes for a reviews integration

- Poll per location on a schedule, newest first, and stop paging when you reach a review you already have. Store `id` as your dedupe key.
- On Launch, ten locations polled once is a full minute of budget. Spread polling across the hour or use the `interaction.review` webhook instead.
- Auto replies are public and permanent on the review site. Require a human approval step or a strict rating threshold, and never auto reply to reviews below four stars.
