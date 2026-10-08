# Skills CLI distribution

The public source is `https://github.com/listings-api/listingsapi-mcp`. Keep the four workflow skills and the existing integration skill under `skills/`, each with its own `SKILL.md` and bundled license. The general `listingsapi` skill remains available separately.

## Prepared skill set

| Skill | Directory |
| --- | --- |
| Listing audit | [`skills/listingsapi-listing-audit`](../skills/listingsapi-listing-audit/SKILL.md) |
| Review management | [`skills/listingsapi-review-management`](../skills/listingsapi-review-management/SKILL.md) |
| Multi-location posting | [`skills/listingsapi-multi-location-posting`](../skills/listingsapi-multi-location-posting/SKILL.md) |
| Performance reporting | [`skills/listingsapi-performance-reporting`](../skills/listingsapi-performance-reporting/SKILL.md) |
| Existing integration skill | [`skills/listingsapi-integration`](../skills/listingsapi-integration/SKILL.md) |

The integration skill retains its `name` and has its canonical source under `skills/`. Its original root directory is a generated compatibility copy so existing file URLs keep working. Run `python3 scripts/package-integration.py` after editing the canonical source; the root copy and ZIP must match it byte for byte.

## Validation and release

1. Validate frontmatter, unique names, folder/name agreement, bundled references, relative links, and ZIP parity. Check that all five requested skills are under a standard discovery directory.
2. Check examples against the intended API specification and MCP catalog. Use offline fixtures for approval boundaries, incomplete reads, queued writes, and partial publisher results. Static or mocked checks do not establish that a real customer workflow succeeded.
3. Review the Git diff and preserve unrelated changes. Confirm the public repository's current default branch before merging the reviewed change. Skill publication does not require a product deployment.
4. After publication is authorized, use a normal fast-forward push when the repository permits it, or follow its required pull-request process. Preserve branch protections and required checks; never force-push to publish skills.
5. After the public source is available, verify discovery with an authorized Skills CLI run, then perform a genuine installation for a user who wants it. Do not install repeatedly to manufacture telemetry or claim that pushing alone guarantees indexing. No package installation or live authentication is part of the offline validation stage.

Commands for a later authorized CLI check:

```bash
npx skills add listings-api/listingsapi-mcp --list
npx skills add listings-api/listingsapi-mcp --skill listingsapi-listing-audit
npx skills add listings-api/listingsapi-mcp --skill listingsapi-review-management
npx skills add listings-api/listingsapi-mcp --skill listingsapi-multi-location-posting
npx skills add listings-api/listingsapi-mcp --skill listingsapi-performance-reporting
npx skills add listings-api/listingsapi-mcp --skill listingsapi-integration
```

These are release instructions, not evidence that publication or installation occurred. Report the actual public commit, tested CLI version, install outcome, and observed skills.sh URLs separately. Do not promise an indexing deadline.

## Contract and metric limitations

The initial workflow contracts were checked against the maintained API specification, MCP catalog, and the corresponding public-guide sources on 2026-10-08. Recheck changed contracts before release; a source snapshot is not proof of production behavior.

The analytics schemas document fields and bucket shapes but do not establish current publisher support, ingestion delay, or retention. The reporting skill treats uncertain recent Google data, Facebook action fields, and Bing series as unverified until availability and freshness are established. It excludes unavailable or provisional zeros from trend conclusions. No private communications or customer data belong in this package.

## Validation record: 2026-10-08

- The five requested skills pass required frontmatter, name/folder agreement, license, and standard-discovery checks. All six repository skills pass the bundled skill-creator validator. The unchanged general skill retains its existing OpenClaw-specific nested metadata; the five requested skills use the portable Agent Skills fields.
- Relative Markdown links resolve. Named workflow tools match the exposed MCP tool inventory, and explicit workflow routes exist in the SDK specification. New location and campaign JSON bodies validate against that specification; all Python and JSON code blocks parse.
- Offline Python transport checks cover nested errors, `success: false`, missing created records, read rate-limit recovery, no blind write retries, malformed/repeated cursor handling, incomplete offset pages, preserved null analytics, and key redaction in object representation. Onboarding fixtures cover existing-record reuse, ambiguous matches, request wrappers, and pending listing states.
- The TypeScript scaffold passes strict compilation with TypeScript 5.9.3 and equivalent mocked transport checks. The existing installed compiler was used; no package was installed.
- An independent agent simulated all five requested workflows with partial access, review prompt injection, changed campaign targets, mixed publisher results, provisional analytics, and unapproved onboarding. Its findings about uncertain-write retries and incomplete pagination were corrected and covered by the offline checks.
- The integration ZIP matches all 14 files of its source directory, with valid CRCs and no extra entries. The five skill license files match the root MIT notice; the general skill and its MIT-0 license are unchanged. A targeted credential-pattern scan found no matches.

The public MCP release base was verified as `46ffbc1870ee820d64e1de3b9d354e411ad2a032`, and the maintained contract source matched the version used for validation. No authenticated customer API call, OAuth grant, Skills CLI installation, push, pull request, or publication was performed during the offline validation phase. Metric freshness and current upstream availability remain unverified; the skills expose that uncertainty rather than treating schema fields as service guarantees.

## Official references

- [Agent Skills format](https://agentskills.io/specification)
- [Skills CLI options and discovery directories](https://github.com/vercel-labs/skills)
- [skills.sh listing and telemetry FAQ](https://skills.sh/docs/faq)
