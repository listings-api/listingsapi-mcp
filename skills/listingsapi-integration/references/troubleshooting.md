# Troubleshooting

| Symptom | Actual cause | Fix |
| --- | --- | --- |
| `POST /locations` returns errors with `SY10005` | `description` is under 200 characters | Supply a real description of 200 plus characters. Most store records do not have one; decide where it comes from before the backfill |
| `POST /locations` returns `SY10126: City is Mandatory` | `city` omitted for a country with city level addressing | Send `city`, or set `hideAddress: true` for a service area business |
| `POST /locations` returns `SY10151` nested | Plan location cap reached (Launch 4, Growth 25) | Upgrade or archive a location |
| Create returned HTTP 200 and the code treated it as success, but no location exists | Nested `data.createLocation.errors` was not read | Check `errors` at top level and under `data.<op>` on every write |
| Analytics endpoint returns `null` metrics or `[]` | Publisher profile not connected or not matched to the location, not "no data" | Check the publisher's entry in `GET /locations/{id}/listings/premium` for `connectedAccountId`; run the connect and match flow |
| Reply to review returns errors, or stays `CREATED` forever | Publisher account not connected or matched, or connection stale (`connectivityIssue`) | Connect and match, or reconnect the account |
| Reply fails with `SY50121` | Google allows one owner reply per review | Use the edit endpoint instead of a second respond |
| Write call fails with `SY90016: Write operations not permitted for read-only API key` (HTTP 400) | The key is Read access | Create a Write key in the dashboard. Do not retry with the Read key |
| 401 `SY90005: Invalid Token` on every call | Key wrong, revoked, pasted with a stray space, or sent with `Bearer` instead of `API` | Use `Authorization: API <key>`, regenerate the key |
| 401 after working for weeks | The key was revoked in the dashboard, or the account is past due | Ask for a new key; per tenant apps mark the tenant disconnected |
| 429 while syncing | One request per location in a loop, or parallel pagination, on a 10 per minute plan | Add a token bucket under the plan limit, page sequentially, sleep `retry_after_seconds` on 429 |
| 429 on the `hour` or `day` window | Polling too often | `limiting_window` in the 429 body names the window. Poll on a schedule measured in minutes or hours |
| Cannot create a sixth API key, `SY90079` | Five active keys per account | Revoke an unused key. Budget keys per environment |
| Bearer token works for MCP but REST returns 401 | OAuth tokens are only accepted by `/mcp` | REST needs an API key with the `API` scheme |
| GBP listing create returned `success: true` but nothing on Google | Creation is asynchronous and the response only means accepted. It also returns `success: true` for a bogus `connectedAccountId` | Poll `GET /locations/{id}/listings/premium` and read the Google entry's `syncStatus`, `verified` and `listingUrl` over hours and days |
| `POST /posts` or `create/gmb-listing` returns 400 `Variable "$input" of required type ... was not provided` | Body not wrapped in `input` | Wrap it. Also upgrade SDKs older than Python 0.5.3 or Node 0.3.2 for posts |
| Post stays `INPROGRESS`, `submissionError` set | Publisher not matched for one of the locations, or media URL unreachable | Read `publishDetails[].submissionError` per site |
| Paging loop processes nothing | Cursor loop against an offset endpoint, or the reverse | Check the response example: `edges` vs `records` vs plain array |
| Connected account listings show the wrong account's listings | `connectedAccountId` sent as a query parameter | Send it in the JSON body |
| `connect-listing` returns `did you mean locationId?` | Field named `listingId` | The field is `connectedAccountListingId` |
| Special hours not published | Regular seven day hours missing | Send the full `MONDAY` to `SUNDAY` week alongside any `SPECIAL` entry |
| Duplicate locations after a retry | Writes have no idempotency key | Read back by `storeId` before repeating a create |
| Analytics call returns 200 with `data.googleInsights: null` and `errors` | Path id is neither numeric nor a valid base64 id | Use `databaseId` or the base64 `id` |

When none of these match: capture the full response body, the HTTP status, the timestamp, and the `correlation_id` if the body has one, and email `support@listingsapi.com`.
