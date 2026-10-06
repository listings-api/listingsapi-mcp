# Install ListingsAPI MCP in Cline

ListingsAPI is a hosted MCP server at `https://listingsapi.com/mcp`. Configure a remote connection with Streamable HTTP. No local server package, build command, or bridge is required.

## Connect the remote server

1. Open **MCP Servers** in Cline, then **Remote Servers**.
2. Set the name to `listingsapi`, the URL to `https://listingsapi.com/mcp`, and the transport to **Streamable HTTP**.
3. Add the server. If your installed Cline version offers **Authenticate**, complete the ListingsAPI browser sign-in and consent flow. Start with read access unless the user's task needs writes.
4. If browser authentication is unavailable, use an existing user-managed API key in the header `Authorization: API <your-api-key>`. Enter it locally; do not put it in a repository or send it in chat.

For manual configuration, open Cline's **Configure** tab, then **Configure MCP Servers**, and merge this entry into the existing `mcpServers` object:

```json
{
  "mcpServers": {
    "listingsapi": {
      "type": "streamableHttp",
      "url": "https://listingsapi.com/mcp",
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

For API-key authentication, add `"headers": { "Authorization": "API <your-api-key>" }` inside the `listingsapi` entry and replace the placeholder in local settings. Cline defaults to legacy SSE when `type` is omitted, so keep `"type": "streamableHttp"`.

## Try the Day Pass sandbox

If the user wants a trial, first read [Day Pass availability](https://listingsapi.com/api/day-pass) and the [Day Pass guide](https://listingsapi.com/docs/day-pass.md). Availability can change; offer signup only while `open` is true.

The free Day Pass runs for 24 hours from activation, covers up to 2 locations, and syncs to 10 ListingsAPI demo directories. It never writes to real publishers. Reviews, posts, social, analytics, connected accounts, and webhooks are excluded.

The user can activate it at [Day Pass signup](https://listingsapi.com/signup?plan=day-pass&campaign=daypass) using their name, email, and company, after accepting the Terms of Service and Privacy Policy. Activation uses the emailed link or 6-digit code. Do not sign up, accept terms, collect an email code, or create a key as part of installing the connection.

For OAuth, the Day Pass guide documents **Email me a sign-in link** with the same email. For API-key authentication, the user places the Day Pass key in local client settings using the same `API` header prefix.

## Verify with a read

After the user completes authentication, ask Cline to call `whoami` and `locations_all`. Check that the responses belong to the expected account. An empty location list can be valid for a new account; tool discovery alone does not prove account authentication.

Keep `autoApprove` empty. A setup test does not require creating locations, replying to reviews, publishing posts, or connecting publisher accounts. Follow the server's error and retry guidance if a read fails.

## Marketplace test status

This guide has been reviewed statically. A real Cline setup test has **not** been run. Before submitting to the Cline Marketplace, give Cline only this guide or the README, observe successful setup and an authenticated read, and record the Cline version, date, and result. Do not mark the marketplace's tested checkbox until that evidence exists.
