# Response envelope and pagination

## The envelope

Every response is a GraphQL shaped JSON object. The payload is under `data`, keyed by the operation name, which is not the URL path. You have to know the key for each endpoint. Response examples on each docs page show it.

```json
{
  "data": {
    "allLocations": {
      "edges": [{ "cursor": "TG9jYXRpb246MTgwMDI4OQ==", "node": { "id": "TG9jYXRpb246MTgwMDI4OQ==", "name": "Jenny Home" } }],
      "pageInfo": { "endCursor": "TG9jYXRpb246MTgwMDI4OQ==", "hasNextPage": false, "total": 1 }
    }
  }
}
```

Common data keys:

| Endpoint | Key under `data` |
| --- | --- |
| `GET /locations` | `allLocations` |
| `GET /locations/search` | `searchLocations` |
| `GET /locations-by-store-codes` | `getLocationsByStoreCodes` |
| `POST /locations` | `createLocation` |
| `POST /locations/update` | `updateLocation` |
| `GET /locations/{id}/listings/premium` | `listingsForLocation` |
| `GET /locations/{id}/reviews` | `interactions` |
| `POST /locations/reviews/respond` | `respondToInteraction` |
| `GET /connected-accounts` | `connectedAccountsInfo` |
| `POST /locations/create/gmb-listing` | `createGmbListingForLocation` |
| `POST /posts` | `createSocialPost` |
| `GET /posts/{id}` | `socialPostView` |
| `GET /locations/{id}/google-analytics` | `googleInsights` |
| `GET /locations/{id}/facebook-analytics` | `facebookInsights` |
| `GET /locations/{id}/bing-analytics` | `bingInsights` |
| `GET /sub-categories` | `subcategories` |
| `GET /countries` | `supportedCountries` |

A `data.<key>` of `null` next to a populated `errors` array means the operation failed. See `rate-limits-retries-errors.md`.

## Three list shapes, not one

Check the endpoint's response example before writing a paging loop. A cursor loop against an offset endpoint reads an `edges` key that is never there and silently processes nothing.

### 1. Cursor pages (Relay style)

Parameters `first` and `after`. Response has `edges[].node`, `edges[].cursor` and `pageInfo` with `hasNextPage` and `endCursor`.

Used by: locations list, location search, reviews for a location, the account review rollup.

Loop rule: request one page, process it, then request the next with `after=<pageInfo.endCursor>` while `pageInfo.hasNextPage` is true. Also stop if `edges` comes back empty. Do not issue pages in parallel; that is the most common source of 429s.

`pageInfo` has no `startCursor`. To page backwards use `last` and `before=<cursor of the first edge>`.

Defaults: locations list `first` defaults to 50. Reviews default to 20 and never return the whole history in one call.

### 2. Offset pages

Parameters `page` (1 based) and `perPage`. Response has `records[]` and `pageInfo` with `totalRecords`, `totalPages`, `hasNextPage`, `hasPreviousPage`.

Used by: connected accounts, connection suggestions, connected account listings, posts for a location, bulk posts for a location, the account wide duplicate listings rollup.

Loop rule: increment `page` while `pageInfo.hasNextPage` is true.

### 3. Plain arrays

No pagination. The whole list comes back at once.

Used by: subcategories, countries and states, plan sites, a location's photos, a location's premium listings, locations by ids, locations by store codes.

## IDs

Locations, listings, posts and categories carry two ids:

- `id`: a base64 Relay global id, for example `TG9jYXRpb246MTgwMDI4OQ==`, which decodes to `Location:1800289`.
- `databaseId`: the plain integer, `1800289`.

Rules:

- **Path parameters** such as `/locations/{locationId}/reviews` accept either form. The gateway base64 encodes an all digit value for you.
- **Request bodies** need the base64 `id`: `input.id` on update, `input.locationId` on GBP listing create, `input.locationIds` on posts. Encode it yourself: the base64 of the string `Location:<databaseId>`, as the helpers below do.
- Store the base64 `id` on your own records. It is what every read returns and what every write expects.
- Reviews are different. An interaction's `id` is a plain UUID, used as is.

```python
import base64
def location_gid(database_id: int) -> str:
    return base64.b64encode(f"Location:{database_id}".encode()).decode()
```

```ts
const locationGid = (databaseId: number) =>
  Buffer.from(`Location:${databaseId}`).toString('base64');
```

## Filters and array parameters

Query parameters that take arrays or objects are JSON encoded strings, then URL encoded. `GET /locations-by-store-codes?storeCodes=%5B%22ACME01%22%5D` sends `["ACME01"]`. Reviews take `ratingFilters=[4,5]` and `responseStatus=["PENDING"]` the same way. Build them with your JSON encoder, never by string concatenation.
