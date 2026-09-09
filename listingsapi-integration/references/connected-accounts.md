# Connected accounts

Publisher features run through the account holder's own Google or Facebook credentials. Until the publisher account is **connected** to the Listings API account and its profile is **matched** to the location, three things do not work: replying to reviews on that publisher, publishing posts to it, and reading its analytics. Analytics come back as `null` metrics, not as an error. Check connection state before assuming a feature is broken.

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
4. `POST /connected-accounts/confirm-matches` with `{ "input": { "matchRecordIds": ["<base64 of MatchRecordType:matchedDataDatabaseId>"] } }`.

## Match explicitly

1. `POST /connected-accounts/connected-account-listings` with body `{ "connectedAccountId": "<uuid>", "perPage": 50 }`. The id goes in the **body**; as a query parameter it is ignored and you get another account's listings. Not wrapped in `input`. Offset paged under `data.connectedAccountListings.records`; each has an `id`.
2. `POST /connected-accounts/connect-listing` with `{ "input": { "locationId": "<base64>", "connectedAccountId": "<uuid>", "connectedAccountListingId": "<id from step 1>" } }`. The field is `connectedAccountListingId`, not `listingId`. Response has `success` and `message`.

`SY81068` means that listing is already linked to a location. `SY81070` means the listing does not belong to the connected account you named.

## Create a Google Business Profile listing

For a location that has no Google listing at all. Different from connect-listing, which links one that already exists.

```
POST /locations/create/gmb-listing
{ "input": { "locationId": "TG9jYXRpb246MTgwMDI4OQ==", "connectedAccountId": "4f712c17-...", "folderId": "accounts/123" } }
```

`folderId` is optional and comes from `GET /connected-accounts/{id}/folders`. A flat body without `input` is a 400.

Response: `data.createGmbListingForLocation.success: true`. **This means accepted, not live.** Google verifies and provisions on its own schedule, often days. Known behavior: the endpoint returns `success: true` even when `connectedAccountId` is not a real connected Google account, so never treat the response as proof.

Preconditions: the location has a valid name, address and phone; it does not already have a Google listing (one per location); the connected account is `CONNECTED`.

## Check whether a listing is live

`GET /locations/{locationId}/listings/premium?listingType=premium` returns a plain array under `data.listingsForLocation`, one entry per publisher site. Find the entry whose `site.url` is `maps.google.com` and read:

| Field | Meaning |
| --- | --- |
| `syncStatus` | `IN_PROGRESS`, `SYNCED`, `FAILED`, `REQUIRING_ACTION`, `AVAILABLE`, `COMPLETED`, `PENDING_APPROVAL`, `CANNOT_SUBMIT` |
| `displayStatus` | Human readable version, for example "Connect your account to sync the listing" |
| `actionRequired` | `true` when a person has to do something |
| `listingUrl` | The live URL once there is one |
| `verified` | Google verification state |
| `connectedAccountId` | Which connected account owns it, `null` if unmatched |

Poll this on a schedule measured in hours, not seconds. Every location read also returns `googleVerificationStatus: { status, message }`. Webhooks (`listing.submission`, `connection.*`) push the same transitions; see `webhooks.md`.
