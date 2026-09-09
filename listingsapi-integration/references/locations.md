# Locations

A location is the master record. Everything else (listings, reviews, posts, analytics) hangs off its id.

## Create

`POST /locations`. Body is wrapped in `input`. Required:

| Field | Rule |
| --- | --- |
| `name` | Business name |
| `description` | **At least 200 characters.** Shorter fails with `SY10005`. The most common first failure |
| `countryIso` | Two letter ISO, must be supported (`SY10036`). List from `GET /countries` |
| `subCategoryId` | Integer from `GET /sub-categories`. Pick one with `primary: true` |
| `city` | Required where the country has city level addressing (`SY10126`). Optional only for a service area business with `hideAddress: true` |

Strongly recommended at create time, because a location cannot publish without them:

| Field | Note |
| --- | --- |
| `street`, `postalCode`, `stateIso` | Validated against the country. `stateIso` values come from `GET /countries` |
| `phone` | Validated for the country |
| `storeId` | Your own key. Unique per account. Lets you find the record later with `GET /locations-by-store-codes?storeCodes=["ACME01"]` |
| `bizUrl` | Website |
| `businessHours` | Seven entries, one per weekday. See below |
| `primaryGbpSiteCategoryId` | Google category as a GCID such as `gcid:restaurant`, resolved against `countryIso` |

```json
{
  "input": {
    "name": "Acme Kitchen",
    "description": "Acme Kitchen is a family-owned neighborhood restaurant in downtown New York serving wood-fired pizza, hand-rolled pasta, and a short seasonal menu built around produce from nearby growers. Our dining room seats forty, takeout and delivery run until close, and the bar pours regional wine and beer on tap.",
    "storeId": "ACME01",
    "street": "123 Jump Street",
    "city": "New York",
    "stateIso": "NY",
    "postalCode": "10013",
    "countryIso": "US",
    "phone": "6443859313",
    "bizUrl": "https://acmekitchen.example.com",
    "subCategoryId": 1432,
    "businessHours": [
      { "day": "MONDAY", "type": "OPEN", "slots": [{ "start": "09:00am", "end": "05:00pm" }] },
      { "day": "SUNDAY", "type": "CLOSED", "slots": [] }
    ]
  }
}
```

Success: HTTP 200, `data.createLocation.success: true`, `errors: null`, `location.id` is the base64 id to store, `location.status` starts as `PENDING`. Publishing to every site in the plan is queued automatically. Pass `enabledSiteIds` (from `GET /plan-sites`) to publish to a subset.

Failure: HTTP 200 with `data.createLocation.errors` populated, or HTTP 400 for a malformed body. Read both.

Plan caps apply: Launch allows 4 locations, Growth 25. Past the cap the create fails with `SY10151` nested in the errors.

## Business hours

- `day` is `MONDAY` to `SUNDAY` in uppercase, or `SPECIAL` for a dated override with `specialDate` as `YYYY-MM-DD`.
- `type` is `OPEN` or `CLOSED`. Closed days have `slots: []`.
- Slot times are strings like `09:00am` and `05:00pm`.
- Special hours only publish when the full seven day regular week is also present. Google rejects special hours without regular hours.
- `temporarilyClosed: true` stops publishing hours without deleting them.

## Read

| Call | Returns |
| --- | --- |
| `GET /locations?first=50&after=<cursor>` | Cursor page under `data.allLocations` |
| `GET /locations/search?query=<text>&first=50` | Cursor page under `data.searchLocations`. Matches name, street, city, store id |
| `GET /locations-by-store-codes?storeCodes=["A","B"]` | Plain array under `data.getLocationsByStoreCodes`, `null` when nothing matches |
| `GET /locations-by-ids?ids=[...]` | Plain array of full records |

Useful fields on a location node: `id`, `databaseId`, `storeId`, `name`, address fields, `phone`, `subCategoryId`, `approved`, `archived`, `status`, `planName`, `googleVerificationStatus: { status, message }`.

## Update

`POST /locations/update` with `input.id` (base64) plus only the fields that change. Unsent fields are left alone. Any change re-syncs every listing. `businessHours` is replaced as a whole when sent.

## Archive

`POST /locations/archive` schedules archival; `POST /locations/cancel_archive` reverses it before it runs. Archived locations stop publishing and stop counting toward the plan cap.

## Mapping an existing model onto locations

For an app that already has stores or branches:

1. Add two columns to your record: `listingsapi_location_id` (the base64 id) and `listingsapi_synced_at`.
2. Send your record's primary key or store code as `storeId`. It is the recovery path if your stored id is lost.
3. Build one mapper function from your record to the `input` object, and one from a location node back to the fields you mirror. Keep the source of truth decision next to them as a table: for each field, "ours" or "theirs".
4. Description is where mapping usually breaks: most store records have no 200 character description. Decide where it comes from (a template, a CMS field, a generated paragraph reviewed by a person) before the backfill.
5. Categories need a lookup: cache `GET /sub-categories` (thousands of rows, no pagination) and map your category to a `subCategoryId` once.
6. Backfill: iterate your records, skip ones with a stored id, look up by `storeId` first to avoid duplicates, create the rest, one at a time, under the rate limiter.
