# Installing the Listings API MCP

This is a remote MCP server. Do not clone this repository, do not run any build step, and do not install any package. Configuration is the entire installation.

## Step 1: get an API key

Ask the user for their Listings API key. If they do not have one, tell them to create it at https://www.listingsapi.com/pricing and wait for them to supply it. Never invent or guess a key.

If the user has no key and wants to try the server first, check `GET https://listingsapi.com/api/day-pass`. While `open` is true you can start a free 24-hour sandbox day pass for them by following https://listingsapi.com/docs/day-pass.md: it needs their first name, last name, email and company, their agreement to the Terms of Service, and then either the 6-digit code from the email or their press of Start my day pass in it. The user can also sign up in the browser at https://listingsapi.com/signup?plan=day-pass&campaign=daypass. The day pass returns an API key, starting with `dp.`, for the configuration below. It covers locations and listings only, and syncs only to demo directories.

## Step 2: add the server to the MCP settings

Add this entry to the `mcpServers` object in the Cline MCP settings file, replacing `<your-api-key>` with the key the user gave you:

```json
{
  "mcpServers": {
    "listingsapi": {
      "url": "https://listingsapi.com/mcp",
      "headers": {
        "Authorization": "API <your-api-key>"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Use the streamable HTTP transport. Do not set a `command` or `args`, there is no local process to start.

## Step 3: confirm it works

Ask the server to list the user's locations. A successful response returns location records. If the response is a 401, the key is wrong or lacks access. If it is a 429, the plan rate limit was hit, wait for the number of seconds in `retry_after_seconds` and try again.

## Notes

- Read operations need a key with Read access. Creating, updating, replying and publishing need Write access.
- Replying to reviews, publishing posts and reading publisher analytics require the matching Google or Facebook profile to be connected and matched to the location first.
