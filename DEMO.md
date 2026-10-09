# Runnable example

Run `python demo.py`; it exercises the exact source API and fails if the intended positive/negative result changes. The installed CLI is separately exercised by `python verify.py` from outside the source directory.

Commands in `smoke.json` document the expected exit status for good, findings/replay and malformed-input cases. Snapshot files are synthetic and intentionally contain no credentials or private production data.

Verify exact raw bytes using Standard Webhooks v1 HMAC, check timestamp window, then atomically claim signed IDs in SQLite; invalid signatures never create/open the ledger.

One configured symmetric key and v1 only; no asymmetric v2, rotation, HTTP server, proxy, queue, provider-specific SDK or side-effect transaction. Message IDs restricted to ASCII letters/digits/underscore/hyphen; timestamp canonical unsigned decimal. Payload 1 MiB, header 4096 characters, default clock tolerance 300 seconds. Claims expire at max(receive time,signed time)+tolerance; signed IDs can be reused after expiry. This is bounded replay-window deduplication, not permanent exactly-once delivery. SQLite only coordinates processes sharing the same local file on a supported filesystem; no network filesystem guarantee. A successful claim followed by a crashed consumer can lose processing; integrate application persistence deliberately. Database stores IDs and expiry, not payloads. Protect secret/ledger permissions and use a trusted clock.
