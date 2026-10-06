# Cline Marketplace issue draft

Title: Add ListingsAPI MCP

Repository: https://github.com/listings-api/listingsapi-mcp

Logo: upload [`logo-400.png`](../logo-400.png), the 400×400 PNG from this repository.

Reason for addition:

ListingsAPI connects Cline to a hosted Streamable HTTP MCP server for business locations, publisher listings, reviews, posts, and local analytics. Users can inspect locations and listing status, summarize reviews, and draft responses using their own account. Public replies and other production writes require the appropriate access and user approval.

The server runs at https://listingsapi.com/mcp and needs no local server package or build. The README and llms-install.md describe setup, authentication, and a first read. When available, the free Day Pass provides 24 hours for up to 2 locations syncing to 10 ListingsAPI demo directories, with no real publisher writes. Reviews, posts, analytics, and connected accounts are outside that sandbox.

Installation-test confirmation: **Pending. Do not assert that a Cline setup test passed.**

Stable/public-ready confirmation: **Pending the required client test.** Before posting, confirm that the reviewed guide and icon are accessible in the public repository. Publishing the files does not prove that Cline setup works.

Before posting, replace the pending test status with actual evidence: Cline version, test date, which guide was supplied, authentication method, and the successful read result. Never include credentials or private account data in the issue.
