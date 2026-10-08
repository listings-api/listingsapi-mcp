# Analytics

Three documented per-location endpoints, all GET, taking `fromDate` and `toDate` as `YYYY-MM-DD`. The path id can be numeric or base64. The table is a response-contract catalog, not a guarantee that every publisher still supplies every metric.

| Endpoint | Data key | Granularity | Metrics |
| --- | --- | --- | --- |
| `/locations/{id}/google-analytics` | `googleInsights` | Daily | `total`, `search`, `maps`, `directionsAction`, `phoneAction`, `websiteAction`, `businessBookings`, `businessFoodOrders`, `businessFoodMenuClicks` |
| `/locations/{id}/facebook-analytics` | `facebookInsights` | Daily | `views`, `ctaAction`, `directionsAction`, `phoneAction`, `websiteAction` |
| `/locations/{id}/bing-analytics` | `bingInsights` | Weekly | `views` |

Each metric is an array of `{ "startTime": "2025-06-01T00:00:00+00:00", "value": 412 }`. Google's `total` is `search` plus `maps`; it does not include the action metrics.

## What an empty response means

A metric that is `null` (Google, Facebook) or `[]` (Bing) can have several causes; the response alone does not identify which:

1. There is no data for that window.
2. The publisher profile is **not connected or not matched** to this location.

There can also be a publisher freshness or metric-availability gap. A zero-filled series is not proof that a currently supported metric measured zero activity. Check current publisher availability and completeness before using it in a comparison, especially for Facebook action fields and Bing series. When this cannot be verified, label it unverified and exclude it from performance conclusions.

Before explaining an empty result, check `GET /locations/{id}/listings/premium` and the relevant account's connection health. A non-null `connectedAccountId` identifies a link but does not prove metric availability. Offer a connection repair only when the evidence supports it and the user authorizes it.

Treat `null` and `[]` the same way in aggregation code. A request with an id that is neither numeric nor a valid base64 id returns HTTP 200 with `data.googleInsights: null` and an `errors` array, which is easy to mistake for a server fault. Check `errors`.

## Design notes

- Pull once per location per day for daily metrics. On Launch, 4 locations times 3 publishers is 12 requests, so spread them over two minutes or more.
- Cache by location, publisher, metric, and date range, with a refresh policy for delayed or revised data. Recent Google observations may be incomplete. Verify the current freshness window before calling a period final; do not assert a fixed delay or guaranteed retention from a schema alone.
- For a before/after report, use comparable completed periods and report missing or provisional coverage. Correlation after an hours or category change is not proof the edit caused a performance change.
- Review KPIs are a separate endpoint; see `reviews.md`.
