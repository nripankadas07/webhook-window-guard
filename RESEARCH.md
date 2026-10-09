# Brief and comparable review — 9 October 2026

Observation: 9 October 2026, 06:34 UTC. Live connected GitHub queries `webhook signature verification sort:stars; webhook in:name sort:stars` sorted by stars, bounded result pages. Repository star counts fetched separately, with current default-branch code/docs/issues. Highest-star relevant comparable found: **adnanh/webhook (12,175)**. This is not an exhaustive global ranking; HTML-only parsers, unrelated extractors, mobile-only release automation and report-only tools were distinguished by workflow relevance. Stars are discovery signals, not reliability/performance measurements.

Actual user: Small webhook consumers needing a local persistent duplicate guard without a server or queue dependency.

Painful task: Valid signature verification alone does not coordinate concurrent deliveries bearing the same signed message ID.

Smallest useful capability: Verify exact raw bytes using Standard Webhooks v1 HMAC, check timestamp window, then atomically claim signed IDs in SQLite; invalid signatures never create/open the ledger.

Acceptance: good synthetic fixture passes; confirmed contract violation produces actionable JSON/exit 1; malformed input produces exit 2; installed quickstart works outside source; core boundary/concurrency/format regressions pass; remote Python matrix passes before LIVE.

Evidence and demand: The Standard Webhooks specification/SDK documents the v1 signature format. Persistent small-consumer replay claims are an inferred use case, not a verified request or proof that the larger Svix/receiver ecosystems lack deduplication. Need for this exact MVP is inferred, not an upstream request to build it.

Portfolio/distinctness: trustline-mcp governs agent tool calls; this tool authenticates inbound webhook bytes and coordinates local duplicate claims. It is more than a signature-only wrapper: the atomic persistent claim and future-timestamp expiry boundary are tested. Compared all five briefs and 148 current owned repository descriptions and files where overlapping. No fork, rename or product subdivision counted as new.

Discovery: Standard Webhooks replay protection and SQLite deduplication searches; concurrency example.

| Comparable | Stars | Last push UTC | License metadata | Observed workflow/capability tradeoff |
| --- | ---: | --- | --- | --- |
| [svix/svix-webhooks](https://github.com/svix/svix-webhooks) | 3441 | 2026-10-08T22:27:24Z | MIT | Managed/self-hosted webhook service and SDKs with delivery/retries/security; operational service workflow. |
| [standard-webhooks/standard-webhooks](https://github.com/standard-webhooks/standard-webhooks) | 1764 | 2026-10-08T19:27:01Z | Apache-2.0 | Specification plus language SDKs for canonical signatures and timestamp verification; protocol reference. |
| [adnanh/webhook](https://github.com/adnanh/webhook) | 12175 | 2026-09-04T18:02:57Z | MIT | Go HTTP receiver with rules and configured command execution; live server rather than local replay claim library. |

- [svix/svix-webhooks source](https://github.com/svix/svix-webhooks/blob/2f06f3d9bd98249f5f955bde4b23ae4d2d1ceeb9/bridge/svix-bridge/src/webhook_receiver/verification.rs), head `2f06f3d9bd98249f5f955bde4b23ae4d2d1ceeb9`. README `README.md`, source and up to five current issue/PR entries read. Maintenance signal is the dated push, not a guarantee of support. Issue examples: fix(server): probe Redis pool connection eagerly to surface TLS/DSN errors at startup, fix(javascript): honor numRetries: 0 instead of falling back to the default
- [standard-webhooks/standard-webhooks source](https://github.com/standard-webhooks/standard-webhooks/blob/7537d2a2d3d52d8f2e0ecd12527af4a9307fd81b/libraries/python/standardwebhooks/webhooks.py), head `7537d2a2d3d52d8f2e0ecd12527af4a9307fd81b`. README `README.md`, source and up to five current issue/PR entries read. Maintenance signal is the dated push, not a guarantee of support. Issue examples: check in a license file for the java library, chore(deps-dev): bump ruff from 0.15.20 to 0.16.10 in /libraries/python
- [adnanh/webhook source](https://github.com/adnanh/webhook/blob/2bbdeb9f90b5f98c7b7b8976881efd6da9f69571/internal/hook/hook.go), head `2bbdeb9f90b5f98c7b7b8976881efd6da9f69571`. README `README.md`, source and up to five current issue/PR entries read. Maintenance signal is the dated push, not a guarantee of support. Issue examples: Requesting a private channel to report a security issue, Reload TLS certificate and key on change when -hotreload is set

Installability, time to first result, reliability and support comparison: README instructions, examples, current source and issues were reviewed. Competitor clean installations, workload timing, historical support response and demo reliability were **not measured**. Our own clean installation/demo proves only our behavior. NOASSERTION is incomplete license metadata, not a conclusion about permission. Licenses/attribution require actual upstream license review before reuse; no upstream code reused here.

No technical-performance benchmark or superiority claim. Workloads/hardware/versions were not measured equivalently, so stars and a successful example do not imply we outperform these tools. Broader tools already offer valuable workflows; this MVP chooses a small explicit contract with significant limits.
