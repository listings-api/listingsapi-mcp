# Connected accounts

Publisher features run through the account holder's own Google or Facebook credentials. Until the publisher account is **connected** to the Listings API account and its profile is **matched** to the location, three things do not work: replying to reviews on that publisher, publishing posts to it, and reading available analytics. Empty metrics can also reflect availability or freshness gaps; a connection check alone does not prove the cause.

## The two step model

1. **Connect** a Google or Facebook account. This is an OAuth flow the end user completes in a browser. The API mints the URL; your app sends the user to it.
2. **Match** the profiles in that account to your locations, either automatically (trigger matches, then confirm suggestions) or explicitly (connect a specific listing to a specific location).

## Connect

Two ways to mint the OAuth URL. Both take absolute HTTPS redirect URLs you control.

| Call | Scope | Body |
| --- | --- | --- |
| `POST /connected-accounts/connect-google` (or `connect-facebook`) | Whole account, then match many | `{ "input": { "successUrl", "errorUrl" } }` |
| `POST /locations/oauth_connect_url` | One location | `{ "input": { "locationId", "site": "GOOGLE" or "FACEBOOK" or "APPLE", "successUrl", "errorUrl" } }` |

Response: `data.<op>.url` is single use. Send the user there. On return to `successUrl`, read `GET /connected-accounts` to confirm. Check `url` is non null; a relative redirect URL comes back as `success: true` with `url: null`.

## List and inspect

`GET /connected-accounts?page=1&perPage=20` is offset paged under `data.connectedAccountsInfo.records`. Each record has `connectedAccountId` (a UUID, the id every other call wants), `connectedAccountType` (`GoogleAccount`, `FacebookAccount`), `status` (`CONNECTED` and others), `connectivityIssue`, `connectedLocationsCount`, `requestMatchesStatus`.

## Match automatically

1. `POST /connected-accounts/trigger-matches` with `{ "input": { "connectedAccountIds": ["<uuid>"] } }`. Queues a fetch and match job. `failedIds` lists accounts that could not be queued.
2. Poll `GET /connected-accounts` until `requestMatchesStatus` is `MATCH_COMPLETED`.
3. `GET /connected-accounts/{connectedAccountId}/connection-suggestions` (offset paged). Each record pairs a `locationId` with a suggested publisher listing and carries `matchedDataDatabaseId`.
4. Review the suggested location/profile pairs and obtain explicit approval for the exact matches. Then call `POST /connected-accounts/confirm-matches` with `{ "input": { "matchRecordIds": ["<base64 of MatchRecordType:matchedDataDatabaseId>"] } }`.

## Match explicitly

1. `POST /connected-accounts/connected-account-listings` with body `{ "connectedAccountId": "<uuid>", "perPage": 50 }`. The id goes in the **body**; as a query parameter it is ignored and you get another account's listings. Not wrapped in `input`. Offset paged under `data.connectedAccountListings.records`; each has an `id`.
2. `POST /connected-accounts/connect-listing` with `{ "input": { "locationId": "<base64>", "connectedAccountId": "<uuid>", "connectedAccountListingId": "<id from step 1>" } }`. The field is `connectedAccountListingId`, not `listingId`. Response has `success` and `message`.

`SY81068` means that listing is already linked to a location. `SY81070` means the listing does not belong to the connected account you named.

## Create a location from a listing

For a Google or Facebook listing that has no location yet. This creates the location from the publisher's data and links it to the listing.

```
POST /connected-accounts/create-location-from-listing
{ "input": { "connectedAccountId": "4f712c17-...", "connectedAccountListingId": "<id from connected-account-listings>", "enabledSiteIds": [384, 180], "submissionDisabledSiteIds": [180] } }
```

`enabledSiteIds` and `submissionDisabledSiteIds` are optional, and either can be sent without the other. Without them the location is created against every site in the plan. `enabledSiteIds` limits the listings to those sites; IDs outside the plan are ignored. `submissionDisabledSiteIds` keeps a site's listing but does not submit the location to it. Take site IDs from `GET /plan-sites` and show the user the intended publisher scope before creating.

Set the sites on this call. Order items are generated shortly after creation, and a later `POST /locations/update` does not withdraw ones that already exist.

Response: `data.createLocationFromConnectedAccountListing` with `success`, `locationId` (the numeric database ID) and `errors`. A Google import is not resubmitted to Google; its listing stays `IN_PROGRESS` until the first location update.

## Create a Google Business Profile listing

For a location that has no Google listing at all. Different from connect-listing, which links one that already exists.

```
POST /locations/create/gmb-listing
{ "input": { "locationId": "TG9jYXRpb246MTAx", "connectedAccountId": "4f712c17-...", "folderId": "accounts/123" } }
```

`folderId` is optional and comes from `GET /connected-accounts/{id}/folders`. A flat body without `input` is a 400.

Response: `data.createGmbListingForLocation.success: true`. **This means accepted, not live.** Google verifies and provisions on its own schedule, often days. Validate the account and location from fresh reads before creating; acceptance is not proof of a live or verified listing.

Preconditions: the location has a valid name, address and phone; it does not already have a Google listing (one per location); the connected account is `CONNECTED`.

## Check whether a listing is live

`GET /locations/{locationId}/listings/premium` returns a plain array under `data.listingsForLocation`, one entry per publisher site. Find the entry whose `site.url` is `maps.google.com` and read:

| Field | Meaning |
| --- | --- |
| `syncStatus` | `IN_PROGRESS`, `SYNCED`, `FAILED`, `REQUIRING_ACTION`, `AVAILABLE`, `COMPLETED`, `PENDING_APPROVAL`, `CANNOT_SUBMIT` |
| `displayStatus` | Human readable version, for example "Connect your account to sync the listing" |
| `actionRequired` | `true` when a person has to do something |
| `listingUrl` | The live URL once there is one |
| `verified` | Google verification state |
| `connectedAccountId` | Which connected account owns it, `null` if unmatched |

Poll this on a schedule measured in hours, not seconds. Every location read also returns `googleVerificationStatus: { status, message }`. Webhooks (`listing.submission`, `connection.*`) push the same transitions; see `webhooks.md`.
