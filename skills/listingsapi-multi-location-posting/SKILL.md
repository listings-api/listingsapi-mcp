---
name: listingsapi-multi-location-posting
description: Prepare, schedule, and publish approved ListingsAPI announcements, events, or offers to Google Business Profile and Facebook across selected business locations, then verify publisher outcomes. Use for location-based campaigns, not the separate brand-based Social API.
license: MIT
---

# ListingsAPI multi-location posting

Prepare a campaign with explicit locations, publishers, copy, media, and timing. Publish only the concrete campaign the user approves.

## Preflight the campaign

Use an existing MCP connection to `https://listingsapi.com/mcp` or an existing REST integration at `https://listingsapi.com/api/v4`. MCP accepts its client OAuth flow or `Authorization: API <key>`; REST uses the API header. Keep credentials in the existing secret store or environment. Publishing needs write access. Day Pass excludes posts.

Resolve the requested locations with `locations_search`/`locations_all` and retain returned Relay IDs. Read all pages needed for a region, tag, or account-wide target. Do not treat a first page as the entire campaign audience. If a cursor repeats, a page is missing, or access fails, label the target list incomplete and resolve it before publication.

For every intended location/publisher pair, check `listings_premium` and, where needed, `connected_accounts_list`. Google and Facebook profiles must be connected and matched. A connected account without a matching location is insufficient. Report blocked targets; changing the approved target set requires approval, including sending only to the ready subset.

Confirm the post type, per-site message, CTA and destination, media URL, and any event or offer terms. Media must be user-approved and publicly retrievable by the publisher; do not upload or make private assets public implicitly. For scheduling, resolve timezone and exact start/end instants. Offer validity dates are distinct from the post's publication window. Use current event/offer schemas rather than guessing fields.

## Build the supported request

| Task | MCP tool | REST operation |
| --- | --- | --- |
| Create one campaign for one or many locations | `posts_create_social` | `POST /posts` |
| Read campaign status | `posts_social_post_view` | `GET /posts/{postId}` |
| Find existing posts for a location | `posts_rollup_social_posts_by_location` | `GET /locations/{locationId}/posts` |

Read the discovered MCP schema before calling. The REST create body wraps fields under `input`; MCP exposes typed named arguments and handles that wire wrapper. Use `locationIds` for multiple locations. Do not invent a separate MCP bulk-post tool: redundant `/bulk-posts` aliases are excluded from the catalog. Brand-based `social_*` operations have different IDs and contracts and do not replace this flow.

Read [the request example](references/campaign-example.md) when constructing a payload. `postSites` is `GOOGLE`, `FACEBOOK`, or both, with a `postMessage` entry for each selected site. Resolve IDs and dates from the user and actual reads, never from the example.

## Approve, submit once, verify

Show the exact location list/count, publishers, final copy per site, media, CTA, offer/event details, and publish/removal times with timezone. Obtain explicit approval for that campaign. Prior approval is sufficient only if it covers those exact values. A request to draft, preview, or prepare does not authorize a write.

Recheck affected connection or target changes before submitting. Inspect HTTP status, top-level errors, and `data.createSocialPost.errors`/`success`. Save the returned `socialPost.id`. A timeout or 5xx can hide a committed create: inspect known post IDs or the target locations' post lists before considering another attempt. If the outcome cannot be established, stop and report uncertainty; do not duplicate a campaign.

Read `data.socialPostView.socialPostInfo` for status. `SCHEDULED` is queued for the specified time; `INPROGRESS` is still running. Even `SUCCESS` is not proof that every publisher accepted the post: inspect `publishDetails[].status` (`PUBLISHING`, `PUBLISHED`, `ERROR`), `submissionError`, and `postLinks[]`.

Report only the granularity actually returned. If the API gives site-level results without per-location confirmation, say which location outcomes remain unverified. Give the campaign ID, confirmed links, pending targets, failures, and any unread results. Honor rate limits, bound status reads, and finish with the latest observed state; do not claim to keep monitoring unless a separate follow-up was requested and scheduled.

## References

- [Publish and schedule location posts](https://listingsapi.com/guides/publish-posts)
- [Announcement request contract](https://listingsapi.com/docs/api/posts-create-announcement)
- [Event contract](https://listingsapi.com/docs/api/posts-create-event) and [offer contract](https://listingsapi.com/docs/api/posts-create-offer)
