<p align="center">
  <img src="logo.svg" alt="ListingsAPI" width="140">
</p>

<h1 align="center">Listings API MCP</h1>

<p align="center">
  Connect any MCP capable AI assistant to the Listings API and manage business listings, reviews, posts and local analytics across 50 plus directories, maps and search engines.
</p>

<p align="center">
  <a href="https://www.listingsapi.com">Website</a> ·
  <a href="https://listingsapi.com/docs">API docs</a> ·
  <a href="https://www.listingsapi.com/mcp">MCP page</a> ·
  <a href="https://claude.ai/directory/listings-api">Claude directory</a> ·
  <a href="https://www.listingsapi.com/pricing">Get an API key</a> ·
  <a href="https://apify.com/listingsapi">Apify actors</a>
</p>

---

## What the Listings API is

Local search runs on business data. A shop, a clinic or a franchise outlet has a name, an address, a phone number, opening hours, categories and photos, and that data has to be identical on Google, Apple Maps, Bing, Facebook, Yelp, the voice assistants and dozens of smaller directories before search engines trust it enough to rank it. Keeping that data consistent by hand does not scale past a handful of locations.

The [Listings API](https://www.listingsapi.com) is a REST API that does this job. You store each location once, and the API syncs it to more than 50 publishers, tracks where each listing is live, finds and suppresses duplicates, pulls in the reviews those listings collect, lets you reply to them, publishes posts and offers to the connected profiles, and returns the performance data Google, Facebook and Bing report back. Agencies, multi location brands and franchise systems use it to run local presence for hundreds or thousands of locations from one place.

## What this MCP server is

The Model Context Protocol lets an AI assistant call external tools. This server exposes the Listings API as a set of MCP tools, so an assistant such as Claude, Cursor, Windsurf, Gemini CLI or Cline can look up your locations, read your reviews, draft and publish replies, schedule posts and pull analytics in plain conversation, using your own account and your own data.

It is a **remote server**. It runs at `https://listingsapi.com/mcp` and uses Streamable HTTP. No local server package or build is required. Point your client at the URL and sign in through its OAuth browser flow, or use an existing API key where the client requires a header.

```
https://listingsapi.com/mcp
```

## Find it in directories

The same server is listed in these directories, so you can install it from the one your client already uses:

| Directory | Listing |
| --- | --- |
| Claude | [claude.ai/directory/listings-api](https://claude.ai/directory/listings-api) |
| Official MCP Registry | [com.listingsapi/mcp](https://registry.modelcontextprotocol.io/?q=com.listingsapi%2Fmcp) |
| Cursor | [cursor.directory/plugins/listings-api](https://cursor.directory/plugins/listings-api) |
| Glama | [glama.ai/mcp/connectors/com.listingsapi/mcp](https://glama.ai/mcp/connectors/com.listingsapi/mcp) |
| Smithery | [smithery.ai/servers/support-hxau/listingsapi](https://smithery.ai/servers/support-hxau/listingsapi) |
| MCP.so | [mcp.so/servers/listings-api](https://mcp.so/servers/listings-api) |
| mcpservers.org | [mcpservers.org/servers/listings-api/listingsapi-mcp](https://mcpservers.org/servers/listings-api/listingsapi-mcp) |

The agent skills in this repository are listed separately; see [Agent skills](#agent-skills).

## What you can do with it

Once connected, the assistant can work across five areas of your account.

**Locations.** Create and update location profiles, search for locations, and read their details. A location is the master record used by its publisher listings.

**Listings and citations.** See which publishers currently carry a location and what state each listing is in, list the sites your plan covers, pull the duplicate listings the network has detected for one location or for your whole account, and mark a listing as a duplicate so it gets suppressed, or clear that flag if the match was wrong. Voice assistant coverage is reported separately.

**Reviews.** Read reviews, fetch specific reviews by ID, inspect review analytics, and publish replies where the connected publisher supports them. Published replies appear on the review site.

**Posts.** Read existing posts and publish posts to supported connected profiles. Check the current tool contract for supported publishers and payloads.

**Analytics.** Read Google, Facebook and Bing performance for any location: search views, map views, direction requests, calls, website clicks and the rest, for whatever date range you ask about.

There is also a set of connected account operations for linking a Google or Facebook account, matching its profiles to your locations and creating a brand new Google Business Profile listing for a location that has none.

Destructive operations such as archiving locations and deleting posts are not exposed as MCP tools. Use the [MCP guide](https://listingsapi.com/guides/connect-an-ai-agent-with-mcp) and the server's documentation tools to check the operations currently available.

### Example requests

Once the server is connected, these are the kinds of things you can ask your assistant.

- "List every location we have in Texas and tell me which ones are missing a phone number."
- "Show me all reviews under three stars from the last week across every store, grouped by location."
- "Draft a reply to the latest Google review for the Austin store, keep it under 60 words, and post it."
- "Publish an offer post about 20 percent off servicing to every location in the Northeast region, running through the end of the month."
- "Compare direction requests and phone calls for our top ten stores this month against last month."
- "Which of our locations still do not have a Google Business Profile listing?"

## What you need

A ListingsAPI account. See [plans and signup](https://www.listingsapi.com/pricing) for production access, or check Day Pass availability below. OAuth-capable clients let you sign in without copying an API key into a configuration file.

### Try it free with a day pass

Check [live availability](https://listingsapi.com/api/day-pass) before signup; the Day Pass is offered for limited periods. While `open` is true, you can activate a free 24-hour sandbox at [Day Pass signup](https://listingsapi.com/signup?plan=day-pass&campaign=daypass). It covers up to 2 locations and syncs to 10 ListingsAPI demo directories. It never writes to real publishers. Reviews, posts, social, analytics, connected accounts, and webhooks are excluded.

Signup asks for your name, email, and company, plus acceptance of the Terms of Service and Privacy Policy. The 24 hours begin when you activate the pass through the emailed link or 6-digit code. Read the [Day Pass guide](https://listingsapi.com/sandbox) for current limits and activation steps. In an OAuth client, choose **Email me a sign-in link** with the Day Pass email. For API-key clients, configure the Day Pass key locally using the same `API` header prefix. Installing a plugin or skill does not start a pass.

Keys carry an access level. A key with Read access covers every lookup and report. Creating and updating locations, replying to reviews, publishing posts and connecting accounts need a key with Write access.

The server accepts two ways of authenticating:

| Method | Header | Use it when |
| --- | --- | --- |
| OAuth 2.0 | Managed by your client | Your client supports the browser sign-in and consent flow |
| API key | `Authorization: API <your-key>` | Your client requires a static header; enter the key only in local settings |

OAuth uses public clients, PKCE, and dynamic client registration. No pre-issued client secret is needed. Start with read access unless your task requires writes. OAuth tokens apply to the MCP endpoint; REST integrations use API keys.

## Setup

Use the client instructions below. Replace API-key placeholders only in local settings, and keep credentials out of shared repositories.

### Codex

In **Add plugin marketplace**, enter:

| Field | Value |
| --- | --- |
| Source | `https://github.com/listings-api/listingsapi-mcp.git` |
| Git ref | `main` |
| Sparse paths | Leave empty |

Choose the **Listings API** marketplace and install **Listings API**. Complete the browser sign-in and consent flow when prompted. The plugin connects to `https://listingsapi.com/mcp` and includes the six [agent skills](#agent-skills) already in this repository. Installation does not create a ListingsAPI account or activate a Day Pass.

To register the same marketplace from the Codex CLI:

```bash
codex plugin marketplace add https://github.com/listings-api/listingsapi-mcp.git --ref main
```

The catalog is [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json), and the Codex compatibility manifest is [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json). They reuse the existing skills, logo, and MCP configuration. Keep sparse paths empty so those files remain available. This repo marketplace is separate from the public OpenAI plugin directory; see the [official packaging documentation](https://developers.openai.com/plugins/build/plugins).

### Claude Code

```bash
claude mcp add --transport http listingsapi https://listingsapi.com/mcp --header "Authorization: API <your-api-key>"
```

### Claude Desktop

Open [claude.ai/directory/listings-api](https://claude.ai/directory/listings-api) and click **Connect**. Claude runs the sign-in flow and the connector is ready in Claude Desktop and Claude.ai.

To add it by URL instead, open Settings, then Connectors, then Add custom connector, and enter `https://listingsapi.com/mcp` as the URL. Claude Desktop will prompt for authentication when the server first requests it.

### Cursor

Install it from [Cursor Directory](https://cursor.directory/plugins/listings-api), or add to `~/.cursor/mcp.json`, or to `.cursor/mcp.json` inside a project:

```json
{
  "mcpServers": {
    "listingsapi": {
      "url": "https://listingsapi.com/mcp"
    }
  }
}
```

Use **Connect** on the server entry to complete OAuth in your browser. This repository's Cursor plugin uses the same configuration. If you need API-key authentication, add `"headers": { "Authorization": "API <your-api-key>" }` inside the entry in local settings.

### Windsurf

Open the MCP configuration file from your editor's MCP settings; the legacy Windsurf location is `~/.codeium/windsurf/mcp_config.json`. Editor versions can use a different path. For a client that supports OAuth, add:

```json
{
  "mcpServers": {
    "listingsapi": {
      "serverUrl": "https://listingsapi.com/mcp"
    }
  }
}
```

Complete the browser authentication prompt. For API-key authentication, add `"headers": { "Authorization": "API <your-api-key>" }` inside the entry in local settings. See the [current Cascade MCP documentation](https://docs.windsurf.com/windsurf/cascade/mcp) for your editor version.

### Gemini CLI

Install this repository as an extension:

```bash
gemini extensions install https://github.com/listings-api/listingsapi-mcp
```

Restart Gemini CLI, then run `/mcp auth listingsapi` and complete the browser sign-in. Use `/mcp` to inspect the connection and discovered tools. The extension enables OAuth and needs no API-key setting.

For an API-key setup instead of the extension, add this entry to the existing `mcpServers` object in `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "listingsapi": {
      "httpUrl": "https://listingsapi.com/mcp",
      "headers": { "Authorization": "API ${LISTINGSAPI_API_KEY}" }
    }
  }
}
```

Provide `LISTINGSAPI_API_KEY` through your local environment. Use one connection configuration at a time. See [Gemini's MCP documentation](https://geminicli.com/docs/tools/mcp-server/) for authentication and configuration details.

### Cline

Open **MCP Servers**, then **Remote Servers**, add `https://listingsapi.com/mcp`, and select **Streamable HTTP**. Complete **Authenticate** if your Cline version offers it. For manual settings, use `"type": "streamableHttp"`; omitting `type` defaults to legacy SSE. The [Cline install guide](llms-install.md) includes the complete configuration, API-key fallback, and a read-only verification procedure.

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

Requests are counted against your Listings API plan, not against this server. The Launch plan allows 10 requests per minute, Growth allows 50, and Enterprise limits are agreed per account. When you go over, the API answers with a 429 and a `retry_after_seconds` value that tells you how long to wait. Every error response also carries a `correlation_id` you can quote to support so they can find the exact request. Full detail is at [listingsapi.com/docs/rate-limits](https://listingsapi.com/docs/rate-limits).

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

## Agent skills

Install the workflows you need from this repository with the [Skills CLI](https://github.com/vercel-labs/skills). Skills supply instructions; they do not configure credentials, grant access, or run customer workflows during installation.

The five workflow skills are listed on [skills.sh](https://www.skills.sh/listings-api/listingsapi-mcp), and the general `listingsapi` skill is on [ClawHub](https://clawhub.ai/listingsapi/skills/listingsapi) for OpenClaw.

```bash
npx skills add listings-api/listingsapi-mcp
```

| Skill | What it does |
| --- | --- |
| [listingsapi-listing-audit](skills/listingsapi-listing-audit/SKILL.md) | Inspect profile completeness, publisher status, live links, and duplicate candidates; produce a prioritized repair plan. |
| [listingsapi-review-management](skills/listingsapi-review-management/SKILL.md) | Triage reviews, draft replies, and publish or edit only approved responses. |
| [listingsapi-multi-location-posting](skills/listingsapi-multi-location-posting/SKILL.md) | Prepare and publish approved Google/Facebook campaigns across selected locations, then verify results. |
| [listingsapi-performance-reporting](skills/listingsapi-performance-reporting/SKILL.md) | Compare performance and reputation with explicit date windows, coverage, and freshness caveats. |
| [listingsapi-integration](skills/listingsapi-integration/SKILL.md) | Integrate REST/SDK authentication, location setup, publisher connections, and submission checks into a new or existing app. |
| [listingsapi](skills/listingsapi/SKILL.md) | General account navigation, connection prerequisites, and Day Pass guidance. |

To choose one skill directly:

```bash
npx skills add listings-api/listingsapi-mcp --skill listingsapi-integration
```

The integration skill retains its existing name. Its canonical source is under `skills/` for standard discovery; the original `listingsapi-integration/` path and ZIP are maintained as compatibility copies. Run `python3 scripts/package-integration.py` after editing the canonical integration skill. Read-only workflows need read access; public replies, campaign publication, profile edits, and publisher connections require approval of the concrete action and write access. Day Pass only covers sandbox locations and demo listings.

See [skills publication notes](marketplaces/skills-sh.md) for validation and release steps. GitHub availability and skills.sh indexing are separate: the [skills.sh FAQ](https://skills.sh/docs/faq) describes discovery through genuine CLI installation telemetry.

## Documentation and support

- Full API reference: [listingsapi.com/docs](https://listingsapi.com/docs)
- MCP server page: [listingsapi.com/mcp](https://www.listingsapi.com/mcp)
- SDKs for Python and Node: [listingsapi.com/sdks](https://listingsapi.com/sdks)
- Agent skill for integrating the API into your own code: [listingsapi-integration](skills/listingsapi-integration/SKILL.md)
- Apify actors for scheduled and no code use: [apify.com/listingsapi](https://apify.com/listingsapi)
- Support: support@listingsapi.com

## About this repository

This repository holds the connection manifests that MCP directories and clients read, plus account workflow and developer integration skills. It contains no product code. The Listings API service itself is closed source and runs at listingsapi.com.

| File | Read by |
| --- | --- |
| `server.json` | The official MCP Registry at registry.modelcontextprotocol.io |
| `gemini-extension.json` | Gemini CLI, when you install this repository as an extension |
| `mcp.json` and `.cursor-plugin/plugin.json` | Cursor, for the marketplace plugin |
| `llms-install.md` | Cline, so it can configure the server on its own |
| `logo.svg` | This README and the directories above |
| `logo-400.png` | Cline Marketplace, which requires a 400×400 PNG |
| `skills/listingsapi/SKILL.md` | A conversational account workflow skill, prepared for ClawHub and compatible skill clients |
| `skills/listingsapi-*/` | Independently installable workflow and developer integration skills |
| `listingsapi-integration/` | Generated compatibility copy of the integration skill, preserving its original file paths |
| `listingsapi-integration.zip` | The `skills/listingsapi-integration/` directory packaged for clients that take a skill upload |

See [marketplace submission notes](marketplaces/README.md) for package paths, submission prerequisites, and current test status. Cursor and Cline setup tests have not been run for these changes.

## License

The manifests in this repository are released under the MIT License. See [LICENSE](LICENSE). Use of the Listings API itself is governed by the [Listings API terms](https://www.listingsapi.com/terms).

The conversational skill in `skills/listingsapi/` is released under [MIT-0](skills/listingsapi/LICENSE) for ClawHub compatibility. The repository's root MIT license and existing integration skill are unchanged.
