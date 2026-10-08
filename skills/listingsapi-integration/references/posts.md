# Posts

Posts publish to a location's Google Business Profile and Facebook Page. Three types: `ANNOUNCEMENT`, `EVENT`, `OFFER`. They need a Write key and the publisher account connected and matched to every location in `locationIds`.

## Create

`POST /posts`. The body **must be wrapped in `input`**. A flat body is a 400 with `Variable "$input" of required type "CreateSocialPostMutationInput!" was not provided`.

```json
{
  "input": {
    "postName": "Grand Opening",
    "locationIds": ["TG9jYXRpb246MTAx"],
    "postType": "ANNOUNCEMENT",
    "postSites": ["GOOGLE"],
    "postMessage": [{ "site": "GOOGLE", "message": "We are now open. Visit us this week." }],
    "postCta": [{ "site": "GOOGLE", "type": "LEARN_MORE", "url": "https://example.com/opening" }],
    "postMediaUrl": [{ "site": "GOOGLE", "url": "https://cdn.example.com/opening.jpg", "type": "IMAGE" }]
  }
}
```

Rules:

- `locationIds` are base64 location ids.
- `postSites` values are `GOOGLE` and `FACEBOOK`. Provide one `postMessage` entry per site you target.
- `postCta.type` is one of `BOOK`, `ORDER`, `SHOP`, `LEARN_MORE`, `SIGN_UP`, `GET_OFFER`.
- Events add start and end dates; offers add coupon and terms fields. See the event and offer pages in the docs for the exact names.
- For many locations, either list them all in `locationIds` or use `POST /bulk-posts` and read the per publisher result back.

## Status

The response is `data.createSocialPost` with `success`, `errors` and `socialPost`. The post starts as `status: INPROGRESS` with `publishDetails[].status: PUBLISHING`. Publishing is asynchronous.

Read `GET /posts/{postId}` using the returned `socialPost.id`. REST nests the result under `data.socialPostView.socialPostInfo`. `SCHEDULED` and `INPROGRESS` remain pending. Even `SUCCESS` does not prove every site accepted it: read each `publishDetails[].status`, `submissionError`, and the returned `postLinks[]`. Do not invent per-location confirmation when only site-level results are present. Bound status reads and report unresolved results.

`GET /locations/{locationId}/posts?page=1&perPage=20` lists a location's posts (offset paged). Multi-location creation uses `locationIds` with `POST /posts`. Its MCP tool is `posts_create_social`; redundant bulk-post aliases are excluded from MCP. Read the runtime schema rather than passing the REST `input` wrapper as an assumed tool argument.

Show the complete campaign and get explicit approval before publishing. A write timeout can hide a successful create: reconcile existing posts before any retry.

## SDK note

The Python SDK from 0.5.3 and the Node SDK from 0.3.2 send the `input` wrapper for posts correctly. Earlier versions sent a flat body and got the 400 above. If `pip show listingsapi` or `npm ls listingsapi-js` reports an older version and the registry does not yet have the newer one, call `POST /posts` directly with the body shown here.
