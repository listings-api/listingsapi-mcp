---
name: listingsapi-performance-reporting
description: Produce read-only ListingsAPI performance and reputation reports across selected locations using Google, Facebook, Bing, review analytics, and listing coverage. Use for period comparisons, location summaries, or identifying missing performance data.
license: MIT
---

# ListingsAPI performance reporting

Build a report with explicit dates, scope, denominators, and data coverage. Reporting does not authorize account connections, profile edits, replies, or post publication.

## Scope the report

Use an existing MCP connection at `https://listingsapi.com/mcp` or the user's REST integration at `https://listingsapi.com/api/v4`. MCP accepts its OAuth flow or `Authorization: API <key>`; REST uses the API header. Read access is sufficient. Keep credentials out of prompts, reports, and logs. Day Pass excludes analytics and reviews.

Resolve the requested locations and comparison periods. State the date windows and relevant timezone; compare like-length complete periods unless the user requests otherwise. Resolve ambiguous location names and dates before calculating. Do not change scope just because some locations are easier to read.

Read runtime tool schemas before constructing requests. Use `search_docs`/`get_doc` or the endpoint docs to verify available metrics and date semantics.

| Data | MCP tool | REST operation |
| --- | --- | --- |
| Google profile metrics | `analytics_google` | `GET /locations/{locationId}/google-analytics` |
| Facebook profile metrics | `analytics_facebook` | `GET /locations/{locationId}/facebook-analytics` |
| Bing profile metrics | `analytics_bing` | `GET /locations/{locationId}/bing-analytics` |
| Review KPIs | `reviews_analytics` | `GET /locations/{locationId}/review-analytics-overview` |
| Review trends | `reviews_analytics_timeline` | Discover the current endpoint/schema |
| Listing coverage | `listings_premium` | `GET /locations/{locationId}/listings/premium` |
| Publisher connectivity | `connected_accounts_list` | `GET /connected-accounts` |

Profile analytics use `fromDate`/`toDate`; review analytics use `startDate`/`endDate`. Google and Facebook return daily metrics; Bing returns weekly `views`. Preserve the returned time buckets and avoid pretending a partial week is a complete daily series.

## Calculate with coverage intact

The data keys are `googleInsights`, `facebookInsights`, and `bingInsights`. Metrics are arrays of `{ startTime, value }`. Google's `total` is `search + maps`; do not add all three and double count impressions. Keep calls, directions, website clicks, and other actions separate. Facebook and Bing views have their own definitions; do not combine them into unique people, revenue, leads, or a comparable cross-publisher ranking.

`null`, empty arrays, omitted metrics, permission errors, and failed requests are missing data, not measured zeros. Check the matching publisher entry and connection state before explaining an empty result; even a healthy connection does not establish why a period is empty. An explicit zero is usable only when the metric is currently supported and the period is sufficiently complete; unsupported, placeholder, or provisional zeros must not become declines. Do not silently turn missing days into zeros or overwrite a previously populated period with an incomplete fetch.

Check freshness and metric availability before calculating. Recent Google data may be delayed or revised; do not assume yesterday is final. Public metric catalogs can lag publisher changes, especially Facebook action metrics and Bing series. If freshness or support cannot be verified, label those series unverified and exclude them from trend conclusions, even when the API returns zeros. Choose a completed comparison window with verified coverage or present observations without claiming a decline. Do not assert a specific delay, retirement date, or guaranteed retention window without a current authoritative source.

Compute period change only for comparable data. Percent change is `(current - previous) / previous * 100` when the previous value is nonzero. If the previous value is zero or either side is unavailable, report absolute change where meaningful and percentage as unavailable. Show coverage changes alongside totals.

Review KPI `value`/`delta` fields describe the requested endpoint's scope. Do not sum average ratings or average per-location percentages without their denominators. Aggregate raw review counts and rating sums only when complete matching records or suitable denominators exist; otherwise retain per-location KPIs. Review rollup is paginated records, not precomputed per-store totals.

## Deliver the report

Include a concise finding, a per-location comparison, observed publisher metrics, review KPIs if requested, and coverage or connection gaps. Every claimed change should be traceable to the fetched period and metric. Before/after correlation does not establish that a listing edit caused the change.

State locations requested/read, date windows, failed or excluded metrics, pagination completeness, and retrieval time. Fetch pages sequentially and respect rate limits with bounded retries. Stop on repeated/missing cursors or authentication failures and label partial results. A report built from a sample must say so. Do not invent estimates to fill unavailable publishers.

Create or share a file only when requested or needed for the deliverable, and do not send it to third parties implicitly. A request for a report now does not create a recurring schedule.

## References

- [Profile analytics guide](https://listingsapi.com/guides/fetch-profile-analytics)
- [Google metrics](https://listingsapi.com/docs/api/profile-analytics-google)
- [Facebook metrics](https://listingsapi.com/docs/api/profile-analytics-facebook)
- [Bing metrics](https://listingsapi.com/docs/api/profile-analytics-bing)
- [Review analytics](https://listingsapi.com/guides/review-analytics)
