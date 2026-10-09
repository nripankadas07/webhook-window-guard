import json, tempfile
from pathlib import Path
import webhook_window_guard as m
SECRET='MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=' # PUBLIC SYNTHETIC DEMO KEY ONLY
with tempfile.TemporaryDirectory() as d:
    ledger=str(Path(d)/'claims.sqlite')
    payload=Path('payload.bin').read_bytes();headers=json.loads(Path('headers.json').read_text())
    first=m.claim(payload,headers,SECRET,ledger,1000)
    second=m.claim(payload,headers,SECRET,ledger,1000)
    assert first['accepted'] and second['reason']=='replay'
    print(json.dumps({'first':first,'duplicate':second},indent=2))
