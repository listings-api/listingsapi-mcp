# Marketplace submission notes

These files prepare ListingsAPI for directory review. They do not publish a listing, authenticate a client, or prove an installation works. Requirements were checked against the linked official sources on 2026-10-06.

## Shared listing fields

| Field | Value |
| --- | --- |
| Name | ListingsAPI MCP |
| Repository | https://github.com/listings-api/listingsapi-mcp |
| Remote endpoint | https://listingsapi.com/mcp |
| Transport | Streamable HTTP |
| Description | Manage business locations, publisher listings, reviews, posts, and local analytics through the hosted ListingsAPI MCP server. |
| Authentication | Public OAuth with PKCE and dynamic client registration where the client supports it; otherwise an existing user-managed key with `Authorization: API <key>`. |
| Documentation | https://listingsapi.com/guides/connect-an-ai-agent-with-mcp |
| Day Pass guide | https://listingsapi.com/sandbox |
| Day Pass signup | https://listingsapi.com/signup?plan=day-pass&campaign=daypass |
| Availability | https://listingsapi.com/api/day-pass |
| Logo | [`logo.svg`](../logo.svg), or [`logo-400.png`](../logo-400.png) for a 400×400 PNG |
| Privacy | https://www.listingsapi.com/privacy |
| Terms | https://www.listingsapi.com/terms |
| Support | support@listingsapi.com |

Production use requires an appropriate ListingsAPI plan. When live availability reports `open: true`, the free Day Pass lasts 24 hours from activation, covers up to 2 locations, and syncs to 10 ListingsAPI demo directories. It never writes to real publishers. Reviews, posts, social, analytics, connected accounts, and webhooks are excluded. Do not describe it as an always-available production trial or a trial of every tool family.

## Packages and publication prerequisites

| Destination | Repository material | Remaining prerequisite |
| --- | --- | --- |
| Cursor Marketplace | [`.cursor-plugin/plugin.json`](../.cursor-plugin/plugin.json), [`mcp.json`](../mcp.json), [`README.md`](../README.md), logo | Run the required local plugin test, publish the reviewed files to the public repository, then sign in at the [publish form](https://cursor.com/marketplace/publish) and submit the repository URL. |
| Gemini CLI Extensions | Root [`gemini-extension.json`](../gemini-extension.json), README | Publish the reviewed manifest and validate an actual extension connection. The public repository already had the `gemini-cli-extension` topic at inspection; no topic mutation is needed. The daily crawler lists extensions only after validation. |
| Cline Marketplace | [`README.md`](../README.md), [`llms-install.md`](../llms-install.md), [`logo-400.png`](../logo-400.png), [issue draft](cline-submission.md) | Run Cline setup from only the README or install guide, observe a successful authenticated read, and record evidence. Publish the files before submitting the [GitHub issue](https://github.com/cline/mcp-marketplace/issues/new?template=mcp-server-submission.yml) from a signed-in account. Leave unverified checkboxes unchecked. |
| Windsurf directory | Endpoint, logo, README connection instructions | The current official Windsurf documentation redirects to Devin Desktop's legacy Cascade guide. Confirm the requested directory and its current submission flow in the parent browser task before filing. No extra manifest is prepared for an unverified directory format. |
| Smithery | Hosted endpoint and shared listing fields | Sign in and use the [URL publishing flow](https://smithery.ai/new). Confirm OAuth scanning succeeds. Current publishing docs describe Client ID Metadata Documents, while the inspected ListingsAPI metadata advertises public PKCE and dynamic registration; their interoperability has not been tested. No local runtime bundle is required for the hosted server. |
| Composio | Hosted endpoint and shared listing fields | The documented Custom MCP flow requires a Composio project and project API authentication. It creates a project-scoped `CUSTOM_*` toolkit, not a public catalog submission. Confirm the intended public integration route with Composio before registering anything. |
| ClawHub / OpenClaw | [`skills/listingsapi/SKILL.md`](../skills/listingsapi/SKILL.md) and its [MIT-0 license](../skills/listingsapi/LICENSE); existing application-integration skill remains separate | Sign in with the selected owner, confirm publication rights, then publish the skill folder. This skill is MIT-0; repository-wide MIT licensing is unchanged. GitHub import requires a public, non-fork repository owned by the signed-in account; local folder publication is a separate route. |
| Glama | Repository URL, endpoint, logo, README | An [existing ListingsAPI entry](https://glama.ai/mcp/servers/listings-api/listingsapi-mcp) was found. The parent task should use its claim/update workflow and verify owner access rather than create a duplicate. |
| MCP.so | Endpoint, name, description, logo, docs | The inspected [remote-server form](https://mcp.so/submit?type=remote-server) offers a $39 paid submission. Skip paid routes. Proceed only if the parent task verifies a free route. |
| PulseMCP | Repository, endpoint, shared listing fields | The inspected [PulseMCP homepage](https://www.pulsemcp.com/) says new server submissions and listing changes are paused. Wait for reopening; a prepared package cannot remove that external blocker. |

## Test evidence required before submission

Static checks cover JSON syntax, documented configuration fields, local paths, skill frontmatter, and PNG dimensions. They do not cover client installation, OAuth callbacks, scope selection, authenticated tool calls, marketplace scans, or review approval.

For Cursor and Cline, record the client version, date, exact guide supplied, authentication method, and result of `whoami` and `locations_all`. Gemini should also show the installed extension and successful `/mcp auth listingsapi`. Use an existing authorized account or a user-activated Day Pass. No publisher write is needed. Tool discovery alone does not establish authentication.

No real Cursor, Gemini, or Cline setup test has been run for this draft. Do not submit a tested or stable-ready attestation until the required evidence exists.

## Official references

- [Cursor plugin format and submission checklist](https://cursor.com/docs/reference/plugins)
- [Cursor MCP configuration and OAuth](https://cursor.com/docs/mcp)
- [Gemini extension reference](https://geminicli.com/docs/extensions/reference/)
- [Gemini gallery discovery](https://geminicli.com/docs/extensions/releasing/#list-your-extension-in-the-gallery)
- [Gemini MCP authentication](https://geminicli.com/docs/tools/mcp-server/)
- [Cline MCP configuration](https://docs.cline.bot/mcp/mcp-overview)
- [Cline Marketplace submission requirements](https://github.com/cline/mcp-marketplace)
- [Current Windsurf / Cascade MCP documentation](https://docs.windsurf.com/windsurf/cascade/mcp)
- [Smithery publishing](https://smithery.ai/docs/build/publish)
- [Composio Custom MCP](https://docs.composio.dev/docs/extending-sessions/custom-mcp)
- [ClawHub skill format](https://github.com/openclaw/clawhub/blob/main/docs/skill-format.md)
- [ClawHub publishing](https://github.com/openclaw/clawhub/blob/main/docs/publishing.md)
- [ListingsAPI MCP guide](https://listingsapi.com/guides/connect-an-ai-agent-with-mcp)
- [ListingsAPI Day Pass guide](https://listingsapi.com/sandbox)
