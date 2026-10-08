---
name: listingsapi-listing-audit
description: Audit ListingsAPI location profiles, publisher sync status, live links, and suspected duplicate listings. Use for a local listing health check, missing listings, or a prioritized repair plan. Keep the audit read-only unless the user approves specific fixes.
license: MIT
---

# ListingsAPI listing audit

Produce an evidence-based health report for the requested locations. An audit does not authorize profile edits, connecting accounts, or duplicate suppression.

## Establish scope and access

Use an already connected ListingsAPI MCP client at `https://listingsapi.com/mcp`, or the user's existing REST integration at `https://listingsapi.com/api/v4`. MCP supports its client OAuth flow or `Authorization: API <key>`; REST uses the API header. Keep credentials in the host's secret store or environment, never in chat or reports. Read access is sufficient for the audit. Do not install software, create credentials, or start a signup as part of it.

Resolve names or store codes with `locations_search` or `locations_all`. Record the returned location IDs and confirm ambiguous matches before continuing. For an account-wide request, page through all locations; otherwise stay within the requested set. A Day Pass can show demo-directory health only; label it as sandbox coverage.

Read available tool schemas before calling them. Use `search_docs` and `get_doc` for the relevant guide, or the linked REST docs below when using an existing API integration. MCP tools expose named fields; REST body wrappers are not automatically MCP arguments.

## Inspect each location

| Evidence | MCP tool | REST operation |
| --- | --- | --- |
| Master profile | `locations_get_locations_by_ids` | `GET /locations-by-ids` |
| Publisher status and live links | `listings_premium` | `GET /locations/{locationId}/listings/premium` |
| Voice coverage, when requested | `listings_voice_assistants` | `GET /locations/{locationId}/voice-assistants` |
| Suspected duplicates | `listings_duplicates` | `GET /locations/{locationId}/listings/duplicates` |
| Account duplicate queue | `listings_duplicates_rollup` | `GET /locations/listings/duplicates` |
| Publisher connection health | `connected_accounts_list` | `GET /connected-accounts` |

Check profile completeness against the user's supplied business facts: name, address, phone, website, description, category, and hours. Missing or inconsistent data is a finding; do not invent a replacement. `businessHours` updates replace the entire supplied schedule, so a future fix must preserve regular and special hours deliberately.

Premium listings return `data.listingsForLocation`. The route already selects premium listings; do not add a `listingType` argument. For each returned publisher, retain `syncStatus`, `displayStatus`, `actionRequired`, `syncIssue` when present, and `listingUrl`.

- `SYNCED` or `COMPLETED`: report the observed status and returned live URL.
- `AVAILABLE`, `IN_PROGRESS`, `PENDING_APPROVAL`: pending, not a completed submission.
- `REQUIRING_ACTION`, `FAILED`, `CANNOT_SUBMIT`: include the publisher's explanation and a concrete next step. Do not treat every failure as a missing connection.
- Missing entries or unreadable responses: unknown coverage, not zero listings.

Duplicate detection is a candidate list, not proof. Read the per-location groups and compare names, addresses, phone numbers, and URLs. Preserve each candidate's `listingItemId`; location IDs and premium-listing IDs are not substitutes. Do not conflate separate branches, practitioners, departments, or businesses at the same address.

## Return findings and optional fixes

Report the scope, retrieval date, locations inspected versus requested, publishers observed, pending/blocked listings, duplicate candidates, and unavailable data. Prioritize customer-facing errors and action-required items. Link evidence and label inferences. A synced percentage must state its denominator; do not present a made-up SEO score or claim ranking gains.

Cursor lists use `first`/`after` and `pageInfo`; duplicate rollups and connected accounts use `page`/`perPage`. Stop on completion. An empty page while more data is pending, or a missing/repeated cursor, means the result is partial; stop and disclose it. Honor `Retry-After`/`retry_after_seconds` with bounded read retries. Report authentication, entitlement, and rate-limit gaps rather than silently omitting locations.

If asked to fix findings, first show the exact field changes or duplicate `listingItemId` values and targets. Obtain explicit approval for that concrete set; existing approval counts only when it covers the same changes. Re-read before applying. `locations_update` can sync edits to publishers; `listings_mark_duplicate` can start suppression. Read back the result, distinguish accepted from finished, and never blindly repeat a timed-out write. Do not bypass missing MCP capabilities with an unapproved REST write.

## References

- [Listing status and live links](https://listingsapi.com/guides/check-listing-status-and-live-links)
- [Find listing errors](https://listingsapi.com/guides/find-and-fix-listing-errors)
- [Duplicate review and suppression](https://listingsapi.com/guides/handle-duplicate-listings)
