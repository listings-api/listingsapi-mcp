# Analytics

Three per location endpoints, all GET, all taking `fromDate` and `toDate` as `YYYY-MM-DD`. The path id can be numeric or base64.

| Endpoint | Data key | Granularity | Metrics |
| --- | --- | --- | --- |
| `/locations/{id}/google-analytics` | `googleInsights` | Daily | `total`, `search`, `maps`, `directionsAction`, `phoneAction`, `websiteAction`, `businessBookings`, `businessFoodOrders`, `businessFoodMenuClicks` |
| `/locations/{id}/facebook-analytics` | `facebookInsights` | Daily | `views`, `ctaAction`, `directionsAction`, `phoneAction`, `websiteAction` |
| `/locations/{id}/bing-analytics` | `bingInsights` | Weekly | `views` |

Each metric is an array of `{ "startTime": "2025-06-01T00:00:00+00:00", "value": 412 }`. Google's `total` is `search` plus `maps`; it does not include the action metrics.

## What an empty response means

A metric that is `null` (Google, Facebook) or `[]` (Bing) means one of two things, and the response does not tell you which:

1. There is no data for that window.
2. The publisher profile is **not connected or not matched** to this location.

Case 2 is the common one in a new integration. Before reporting "no data", check `GET /locations/{id}/listings/premium?listingType=premium` for the publisher's entry: `connectedAccountId` non null and `syncStatus` in a live state means connected. Otherwise send the user through the connect and match flow in `connected-accounts.md`.

Treat `null` and `[]` the same way in aggregation code. A request with an id that is neither numeric nor a valid base64 id returns HTTP 200 with `data.googleInsights: null` and an `errors` array, which is easy to mistake for a server fault. Check `errors`.

## Design notes

- Pull once per location per day for daily metrics. On Launch, 4 locations times 3 publishers is 12 requests, so spread them over two minutes or more.
- Cache by location, publisher and date range. Yesterday's numbers do not change.
- A before and after report (hours or category change, then `search` plus `maps` over the weeks either side) is the common use.
- Review KPIs are a separate endpoint; see `reviews.md`.
