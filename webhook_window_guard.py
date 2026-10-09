"""Standard Webhooks v1 HMAC verification followed by a SQLite replay-window claim."""
import argparse
import base64
import binascii
import hashlib
import hmac
import json
import os
import re
import sqlite3
import time
from pathlib import Path


def authenticate(payload, headers, secret, now, tolerance=300):
    if type(now) is not int or now < 0 or type(tolerance) is not int or not 1 <= tolerance <= 86400:
        raise ValueError('clock must be nonnegative integer; tolerance 1..86400 seconds')
    if not isinstance(payload, bytes) or len(payload) > 1024*1024:
        raise ValueError('payload must be bytes within 1 MiB')
    if not isinstance(headers, dict) or set(headers) != {'webhook-id','webhook-timestamp','webhook-signature'} or not all(isinstance(v,str) for v in headers.values()):
        raise ValueError('supply three exact lowercase Standard Webhooks headers')
    identity = headers['webhook-id']
    stamp = headers['webhook-timestamp']
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,200}',identity) or not re.fullmatch(r'0|[1-9]\d{0,11}',stamp):
        raise ValueError('unsupported message ID or noncanonical timestamp')
    timestamp = int(stamp)
    if abs(now-timestamp) > tolerance:
        return dict(accepted=False, reason='timestamp_window')
    if not isinstance(secret,str):
        raise ValueError('secret must be base64 text')
    try:
        key = base64.b64decode(secret.removeprefix('whsec_'), validate=True)
    except (ValueError,binascii.Error) as e:
        raise ValueError('invalid base64 key') from e
    if len(key) < 32:
        raise ValueError('key must contain at least 32 bytes')
    signature = headers['webhook-signature']
    if len(signature) > 4096:
        raise ValueError('signature header exceeds 4096 characters')
    expected = hmac.new(key, identity.encode()+b'.'+stamp.encode()+b'.'+payload, hashlib.sha256).digest()
    verified = False
    for entry in signature.split():
        if not entry.startswith('v1,'):
            continue
        try:
            raw = base64.b64decode(entry[3:], validate=True)
        except (ValueError,binascii.Error):
            continue
        verified |= hmac.compare_digest(raw, expected)
    if not verified:
        return dict(accepted=False, reason='signature')
    return dict(accepted=True, reason='authenticated', identity=identity, expires=max(now,timestamp)+tolerance)


def claim(payload, headers, secret, ledger, now=None, tolerance=300):
    now = int(time.time()) if now is None else now
    result = authenticate(payload, headers, secret, now, tolerance)
    if not result['accepted']:
        return result  # Invalid input never creates or opens a ledger.
    connection = sqlite3.connect(ledger, timeout=10, isolation_level=None)
    try:
        connection.execute('BEGIN IMMEDIATE')
        connection.execute('CREATE TABLE IF NOT EXISTS webhook_claims (id TEXT PRIMARY KEY, expires INTEGER NOT NULL)')
        connection.execute('DELETE FROM webhook_claims WHERE expires < ?', (now,))
        old = connection.execute('SELECT 1 FROM webhook_claims WHERE id=?', (result['identity'],)).fetchone()
        if old:
            connection.execute('ROLLBACK')
            return dict(accepted=False,reason='replay')
        connection.execute('INSERT INTO webhook_claims(id,expires) VALUES (?,?)', (result['identity'],result['expires']))
        connection.execute('COMMIT')
        return dict(accepted=True,reason='claimed',identity=result['identity'],expires=result['expires'])
    except Exception:
        if connection.in_transaction:
            connection.execute('ROLLBACK')
        raise
    finally:
        connection.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('payload')
    ap.add_argument('headers')
    ap.add_argument('ledger')
    ap.add_argument('--now',type=int)
    ap.add_argument('--tolerance',type=int,default=300)
    args = ap.parse_args()
    try:
        result = claim(Path(args.payload).read_bytes(), json.loads(Path(args.headers).read_text()), os.environ.get('WEBHOOK_WINDOW_SECRET'),args.ledger,args.now,args.tolerance)
        print(json.dumps(result,sort_keys=True))
        return int(not result['accepted'])
    except (ValueError, OSError, UnicodeError, sqlite3.Error) as e:
        # Key material, headers and payload are intentionally not echoed.
        print(json.dumps({'error': 'invalid input or unavailable replay ledger', 'kind': type(e).__name__}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
