# Campaign request example

This fictional example illustrates a Google announcement for two locations. Replace the IDs with returned location IDs and use approved copy and destinations. It is not permission to publish. The IDs encode `Location:101` and `Location:102`.

REST: `POST https://listingsapi.com/api/v4/posts`, with `Authorization: API <key>` supplied securely by the existing client and a JSON body:

```json
{
  "input": {
    "postName": "Autumn opening hours",
    "locationIds": ["TG9jYXRpb246MTAx", "TG9jYXRpb246MTAy"],
    "postType": "ANNOUNCEMENT",
    "postSites": ["GOOGLE"],
    "postMessage": [{ "site": "GOOGLE", "message": "See our updated opening hours before your next visit." }],
    "postCta": [{ "site": "GOOGLE", "type": "LEARN_MORE", "url": "https://example.com/hours" }]
  }
}
```

Omitting `postScheduledDates` requests immediate publication. To schedule, add `postScheduledDates` inside `input`, with approved ISO-8601 `startDatetime` and `endDatetime` values including a timezone offset. Do not reuse example dates for a real campaign. Confirm dates and required type-specific fields against the current contract.

For MCP, inspect `posts_create_social` and pass its named fields, not an assumed REST `input` object. For readback, use `posts_social_post_view` with the returned post ID. Read both the campaign state and publisher entries; report partial acceptance explicitly.
