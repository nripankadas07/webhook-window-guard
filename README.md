# webhook-window-guard

Standard Webhooks v1 HMAC verification and atomic SQLite claims for replay-window deduplication.

## Who and why

Small webhook consumers needing a local persistent duplicate guard without a server or queue dependency. Valid signature verification alone does not coordinate concurrent deliveries bearing the same signed message ID.

Verify exact raw bytes using Standard Webhooks v1 HMAC, check timestamp window, then atomically claim signed IDs in SQLite; invalid signatures never create/open the ledger.

## Quickstart

Python 3.10+ and pip. Git source installation, no external-registry publication:

```sh
git clone https://github.com/nripankadas07/webhook-window-guard.git
cd webhook-window-guard
python -m venv .venv
# Unix: source .venv/bin/activate; Windows: .venv\Scripts\activate
python -m pip install .
python demo.py
# demo sets a PUBLIC SYNTHETIC key, then verifies and rejects a replay
python demo.py
python verify.py
```

CLI JSON on stdout. Exit **0** passes/claims, **1** policy findings or authentication/replay rejection, **2** malformed/unsupported input or IO errors. For automation, inspect the JSON and exit status together. Help: `webhook-window-guard --help`.

The fixture data is entirely synthetic. `demo.py` runs the example without installation and asserts a useful success and failure. `verify.py` additionally checks source tests, compilation and a fresh wheel installation in a temporary environment outside the source directory.

## Input and output

Read the checked-in fixture and policy JSON alongside `webhook_window_guard.py`. Policies reject unknown keys and invalid types rather than silently defaulting. See [DEMO.md](DEMO.md) for exact commands, expected outcome and schema notes; [VALIDATION.md](VALIDATION.md) for measured checks; [RESEARCH.md](RESEARCH.md) for dated comparable evidence and limits.

## Scope and limits

One configured symmetric key and v1 only; no asymmetric v2, rotation, HTTP server, proxy, queue, provider-specific SDK or side-effect transaction. Message IDs restricted to ASCII letters/digits/underscore/hyphen; timestamp canonical unsigned decimal. Payload 1 MiB, header 4096 characters, default clock tolerance 300 seconds. Claims expire at max(receive time,signed time)+tolerance; signed IDs can be reused after expiry. This is bounded replay-window deduplication, not permanent exactly-once delivery. SQLite only coordinates processes sharing the same local file on a supported filesystem; no network filesystem guarantee. A successful claim followed by a crashed consumer can lose processing; integrate application persistence deliberately. Database stores IDs and expiry, not payloads. Protect secret/ledger permissions and use a trusted clock.

## Support

[Support, contribution and security](SUPPORT.md). MIT license. No performance or superiority claim; existing established tools are preferable when you need their broader workflows.
