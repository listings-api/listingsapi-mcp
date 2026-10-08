# First location: read, create, connect, verify

Use this sequence for customer onboarding or as the first vertical slice of an application integration. All sample IDs and business details are fictional. Replace them with verified user data and IDs returned by authorized reads. Never run the example location create against a production account.

The examples use `ListingsAPI` from the Python block in `references/client-scaffold.md`, saved as `listingsapi_client.py`. That block depends on `requests`; reuse the application's existing client when possible, and obtain authorization before installing a dependency. `LISTINGSAPI_KEY` must already be supplied through a secure environment or secret store. The TypeScript client in the same reference exposes equivalent `request`, `locationsByStoreCodes`, and `createLocation` methods.

## 1. Confirm access and look up inputs

```python
from listingsapi_client import ListingsAPI

api = ListingsAPI()
page = api.request("GET", "/locations", params={"first": 5})
locations = [edge["node"] for edge in page["data"]["allLocations"]["edges"]]
# An empty page is valid for a new account; this is only a first-page read.
countries = api.request("GET", "/countries")["data"]["supportedCountries"]
categories = api.request("GET", "/sub-categories")["data"]["subcategories"]
```

Resolve supported country/state values and the matching category's numeric `databaseId`. In MCP, `search_categories` can narrow taxonomy results. Read `GET /plan-sites` to inspect plan coverage; if choosing a subset, use the returned site IDs. Do not log the raw key, authorization header, or full account responses.

## 2. Prepare a location and check for an existing record

Here is the REST body shape for a storefront. The category number is illustrative and must be replaced with a current lookup result. Country-specific exceptions and service-area rules need the current location contract; do not infer that hiding an address means it can be omitted.

```json
{
  "input": {
    "name": "Example Cafe",
    "description": "Example Cafe is an independent neighborhood cafe serving freshly prepared breakfast, seasonal lunches, and coffee throughout the day. Visitors can enjoy comfortable indoor seating, order takeaway meals, and find current menus and opening hours on the cafe website.",
    "storeId": "EXAMPLE-001",
    "street": "100 Example Street",
    "city": "New York",
    "stateIso": "NY",
    "postalCode": "10001",
    "countryIso": "US",
    "phone": "+12125550100",
    "bizUrl": "https://example.com/cafe",
    "subCategoryId": 123
  }
}
```

Create `approved_location` from real business facts only after showing the exact profile and publisher scope to the user and receiving approval. The following function performs a lookup before a single create; it does not handle concurrent workers or authorize itself:

```python
def create_or_find_location(api, approved_location):
    store_id = approved_location["storeId"]
    existing = api.locations_by_store_codes([store_id])
    if len(existing) > 1:
        raise ValueError("Ambiguous store mapping; resolve before writing")
    if existing:
        return existing[0]  # Compare its fields; never overwrite it implicitly.
    return api.create_location(approved_location)
```

Persist the returned location `id` and your `storeId`. Re-read via `GET /locations-by-store-codes` and compare the actual fields with the approved input. If the create times out, perform that lookup before considering another attempt. Absence alone after a timeout may be temporary; stop for reconciliation if you cannot establish the outcome.

## 3. Connect an existing Google or Facebook listing

Only when the user requests this connection, obtain a publisher OAuth URL with `POST /connected-accounts/connect-google` or `/connected-accounts/connect-facebook`. The REST body is `{"input":{"successUrl":"https://example.com/connected","errorUrl":"https://example.com/connection-error"}}`; replace both URLs with HTTPS routes the application owns. Show the URL for the user to complete consent. Do not execute the flow using the illustrative URLs.

After the browser flow, read `GET /connected-accounts` (offset pagination). Select the intended `CONNECTED` account and its returned `connectedAccountId`. Read the profiles using this body; this read endpoint uses POST and does not wrap the fields in `input`:

```python
def read_publisher_profiles(api, connected_account_id):
    return api.request(
        "POST", "/connected-accounts/connected-account-listings",
        body={"connectedAccountId": connected_account_id, "page": 1, "perPage": 20},
    )["data"]["connectedAccountListings"]  # records + pageInfo; fetch further pages as needed.
```

Compare the intended profile's identity and address, show the exact location/profile pair, and get approval before linking. The returned profile `id` becomes `connectedAccountListingId`; it is not a location ID.

```python
def link_approved_profile(api, location_id, account_id, profile_id):
    result = api.request("POST", "/connected-accounts/connect-listing", body={
        "input": {
            "locationId": location_id,
            "connectedAccountId": account_id,
            "connectedAccountListingId": profile_id,
        }
    })["data"]["connectListing"]
    if result.get("success") is not True:
        raise ValueError("Profile was not linked; inspect the sanitized operation error")
    return result
```

For automatic matching, follow the trigger/status/suggestions/confirmation sequence in `references/connected-accounts.md`. Matching completion alone does not link anything. If no Google listing exists, use that reference's Google creation flow only after checking the account and obtaining approval. It is asynchronous and may require user verification.

## 4. Verify submissions and live links

Location creation already queues the configured listings. There is no extra generic submit call in this walkthrough. This read returns a plain array; `listingType` is not a query parameter:

```python
def read_listing_outcomes(api, location_id):
    payload = api.request("GET", f"/locations/{location_id}/listings/premium")
    return [
        {
            "site": row.get("site"),
            "status": row.get("syncStatus"),
            "message": row.get("displayStatus"),
            "action_required": row.get("actionRequired"),
            "url": row.get("listingUrl"),
        }
        for row in payload["data"]["listingsForLocation"]
    ]
```

Report each publisher as observed: synced/completed with its URL, pending, requiring action, failed, or unavailable. Google creation acceptance does not establish that its listing is live. Check status on a bounded, rate-aware schedule; arrange future polling or webhooks only when requested.

Public guides: [add a location](https://listingsapi.com/guides/add-a-location), [connect Google](https://listingsapi.com/guides/connect-google-and-import-locations), [connect Facebook](https://listingsapi.com/guides/connect-facebook-pages), and [listing status](https://listingsapi.com/guides/check-listing-status-and-live-links).
