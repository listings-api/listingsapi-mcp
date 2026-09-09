<p align="center">
  <img src="logo.svg" alt="ListingsAPI" width="140">
</p>

<h1 align="center">Listings API MCP</h1>

<p align="center">
  Connect any MCP capable AI assistant to the Listings API and manage business listings, reviews, posts and local analytics across 50 plus directories, maps and search engines.
</p>

<p align="center">
  <a href="https://www.listingsapi.com">Website</a> ·
  <a href="https://docs.listingsapi.com/docs">API docs</a> ·
  <a href="https://www.listingsapi.com/mcp">MCP page</a> ·
  <a href="https://www.listingsapi.com/pricing">Get an API key</a> ·
  <a href="https://apify.com/listingsapi">Apify actors</a>
</p>

---

## What the Listings API is

Local search runs on business data. A shop, a clinic or a franchise outlet has a name, an address, a phone number, opening hours, categories and photos, and that data has to be identical on Google, Apple Maps, Bing, Facebook, Yelp, the voice assistants and dozens of smaller directories before search engines trust it enough to rank it. Keeping that data consistent by hand does not scale past a handful of locations.

The [Listings API](https://www.listingsapi.com) is a REST API that does this job. You store each location once, and the API syncs it to more than 50 publishers, tracks where each listing is live, finds and suppresses duplicates, pulls in the reviews those listings collect, lets you reply to them, publishes posts and offers to the connected profiles, and returns the performance data Google, Facebook and Bing report back. Agencies, multi location brands and franchise systems use it to run local presence for hundreds or thousands of locations from one place.

## What this MCP server is

The Model Context Protocol lets an AI assistant call external tools. This server exposes the Listings API as a set of MCP tools, so an assistant such as Claude, Cursor, Windsurf, Gemini CLI or Cline can look up your locations, read your reviews, draft and publish replies, schedule posts and pull analytics in plain conversation, using your own account and your own data.

It is a **remote server**. It runs at `https://listingsapi.com/mcp` and speaks the streamable HTTP transport. There is nothing to install, nothing to build and no package to keep up to date. You point your client at the URL, hand it your API key, and the tools appear.

```
https://listingsapi.com/mcp
```

## What you can do with it

Once connected, the assistant can work across five areas of your account.

**Locations.** Create a location with its full profile, update any field, search by name or store code, fetch a set of locations by ID, archive locations you no longer operate, and upload, star or remove the photos attached to each one. This is the master record that everything else keys off.

**Listings and citations.** See which publishers currently carry a location and what state each listing is in, list the sites your plan covers, pull the duplicate listings the network has detected for one location or for your whole account, and mark a listing as a duplicate so it gets suppressed, or clear that flag if the match was wrong. Voice assistant coverage is reported separately.

**Reviews.** Pull every review for a location with its rating, author, text, date and source site, fetch specific reviews by ID, read the review analytics overview for a location, and roll review counts up across the whole account to find the stores with the most unanswered feedback. Then publish a reply, edit it, or archive it. Replies go live on the review site.

**Posts.** Publish an announcement, an event or an offer to a location's Google Business Profile, Facebook Page, Instagram and X, or fan one post out to many locations in a single bulk call and read back the per publisher result. List what has already been published and delete a post that should come down.

**Analytics.** Read Google, Facebook and Bing performance for any location: search views, map views, direction requests, calls, website clicks and the rest, for whatever date range you ask about.

There is also a set of connected account operations for linking a Google or Facebook account, matching its profiles to your locations and creating a brand new Google Business Profile listing for a location that has none.

### Example requests

Once the server is connected, these are the kinds of things you can ask your assistant.

- "List every location we have in Texas and tell me which ones are missing a phone number."
- "Show me all reviews under three stars from the last week across every store, grouped by location."
- "Draft a reply to the latest Google review for the Austin store, keep it under 60 words, and post it."
- "Publish an offer post about 20 percent off servicing to every location in the Northeast region, running through the end of the month."
- "Compare direction requests and phone calls for our top ten stores this month against last month."
- "Which of our locations still do not have a Google Business Profile listing?"

## What you need

A Listings API account and an API key. Create one at [listingsapi.com/pricing](https://www.listingsapi.com/pricing). Plans start at 99 dollars a month and every plan includes a 14 day trial.

Keys carry an access level. A key with Read access covers every lookup and report. Creating and updating locations, replying to reviews, publishing posts and connecting accounts need a key with Write access.

The server accepts two ways of authenticating:

| Method | Header | Use it when |
| --- | --- | --- |
| API key | `Authorization: API <your-key>` | You are configuring a personal client and want the simplest setup |
| OAuth 2.0 | `Authorization: Bearer <access-token>` | You are building a product on top and want per user consent |

Every example below uses the API key method.

## Setup

Replace `<your-api-key>` with your real key in each snippet.

### Claude Code

```bash
claude mcp add --transport http listingsapi https://listingsapi.com/mcp --header "Authorization: API <your-api-key>"
```

### Claude Desktop

Open Settings, then Connectors, then Add custom connector, and enter `https://listingsapi.com/mcp` as the URL. Claude Desktop will prompt for authentication when the server first requests it.

### Cursor

Add to `~/.cursor/mcp.json`, or to `.cursor/mcp.json` inside a project:

```json
{
  "mcpServers": {
    "listingsapi": {
      "url": "https://listingsapi.com/mcp",
      "headers": { "Authorization": "API <your-api-key>" }
    }
  }
}
```

### Windsurf

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "listingsapi": {
      "serverUrl": "https://listingsapi.com/mcp",
      "headers": { "Authorization": "API <your-api-key>" }
    }
  }
}
```

### Gemini CLI

Install this repository as an extension, then export your key:

```bash
gemini extensions install https://github.com/listings-api/listingsapi-mcp
export LISTINGSAPI_API_KEY="<your-api-key>"
```

### Cline

Open the MCP Servers panel and add a remote server with the URL `https://listingsapi.com/mcp` and the header `Authorization: API <your-api-key>`. The file [llms-install.md](llms-install.md) in this repository gives Cline the same instructions in a form it can follow on its own.

### VS Code with GitHub Copilot

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "listingsapi": {
      "type": "http",
      "url": "https://listingsapi.com/mcp",
      "headers": { "Authorization": "API <your-api-key>" }
    }
  }
}
```

### Any other client

Use the streamable HTTP transport with the endpoint and header above. The server does not require SSE.

## Rate limits

Requests are counted against your Listings API plan, not against this server. The Launch plan allows 10 requests per minute, Growth allows 50, and Enterprise limits are agreed per account. When you go over, the API answers with a 429 and a `retry_after_seconds` value that tells you how long to wait. Every error response also carries a `correlation_id` you can quote to support so they can find the exact request. Full detail is at [docs.listingsapi.com/docs/rate-limits](https://docs.listingsapi.com/docs/rate-limits).

A practical note: an assistant that is asked to "check every location" will happily issue a request per location. On the Launch plan that means a pause every ten calls, so scope the question or ask the assistant to work in batches.

## Things worth knowing before you start

**Connected profiles come first.** Replying to a Google or Facebook review, publishing a post and reading publisher analytics all need the matching Google or Facebook profile connected to your account and matched to the location. If an analytics call comes back empty or a reply fails, an unmatched profile is the usual cause. Connect and match first, then run the workflow.

**Listing creation is asynchronous.** When you create a Google Business Profile listing, a successful response means the request was accepted, not that the listing is live. Google verifies and provisions on its own schedule. Check the listing status later rather than assuming it is up.

**Writes are real.** A reply published through this server appears publicly on the review site. A post goes live on the connected profiles. Treat write operations with the same care you would in the dashboard.

**Location descriptions have a floor.** A new location needs a description of at least 200 characters, which is the most common reason a create call fails on its first try.

## Troubleshooting

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| 401 on every call | Key is wrong, expired or pasted with a stray space | Regenerate the key in the API Keys section of your dashboard and update the header |
| 403 on a write | Key has Read access only | Issue a key with Write access |
| 429 | Plan rate limit reached | Wait `retry_after_seconds`, or ask the assistant to work in smaller batches |
| Analytics come back empty | Profile not connected or not matched to the location | Run the connected accounts operations to link and match it |
| Reply accepted but not visible | Review site is still processing it | Give it a few minutes and refresh the review |

## Documentation and support

- Full API reference: [docs.listingsapi.com](https://docs.listingsapi.com/docs)
- MCP server page: [listingsapi.com/mcp](https://www.listingsapi.com/mcp)
- SDKs for Python and Node: [docs.listingsapi.com/sdks](https://docs.listingsapi.com/sdks)
- Agent skill for integrating the API into your own code: [listingsapi-integration/SKILL.md](listingsapi-integration/SKILL.md)
- Apify actors for scheduled and no code use: [apify.com/listingsapi](https://apify.com/listingsapi)
- Support: support@listingsapi.com

## About this repository

This repository holds the connection manifests that MCP directories and clients read, plus an agent skill for developers integrating the API into code. It contains no product code. The Listings API service itself is closed source and runs at listingsapi.com.

| File | Read by |
| --- | --- |
| `server.json` | The official MCP Registry at registry.modelcontextprotocol.io |
| `gemini-extension.json` | Gemini CLI, when you install this repository as an extension |
| `mcp.json` and `plugin.json` | Cursor, for the marketplace listing |
| `llms-install.md` | Cline, so it can configure the server on its own |
| `logo.svg` | This README and the directories above |
| `listingsapi-integration/` | Coding agents such as Claude Code and Codex, as an agent skill for integrating the Listings API into an application. `listingsapi-integration.zip` is the same directory packaged for app directories that take a skill upload |

## License

The manifests in this repository are released under the MIT License. See [LICENSE](LICENSE). Use of the Listings API itself is governed by the [Listings API terms](https://www.listingsapi.com/terms).
