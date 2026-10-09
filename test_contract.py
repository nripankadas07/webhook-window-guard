import base64
import concurrent.futures
import hashlib
import hmac
import tempfile
import unittest
from pathlib import Path
import webhook_window_guard as m

SECRET=base64.b64encode(b'0123456789abcdef0123456789abcdef').decode()


def headers(payload=b'{}', stamp=1000, identity='msg_demo'):
    raw=identity.encode()+b'.'+str(stamp).encode()+b'.'+payload
    sig=base64.b64encode(hmac.new(base64.b64decode(SECRET),raw,hashlib.sha256).digest()).decode()
    return {'webhook-id':identity,'webhook-timestamp':str(stamp),'webhook-signature':'v1,'+sig}


def worker(ledger):return m.claim(b'{}',headers(),SECRET,ledger,1000)['accepted']


class Tests(unittest.TestCase):
    def setUp(self):self.d=tempfile.TemporaryDirectory();self.db=str(Path(self.d.name)/'claims.sqlite')
    def tearDown(self):self.d.cleanup()
    def test_valid_replay(self):
        self.assertTrue(worker(self.db));self.assertFalse(worker(self.db))
    def test_invalid_does_not_create(self):
        self.assertFalse(m.claim(b'changed',headers(),SECRET,self.db,1000)['accepted']);self.assertFalse(Path(self.db).exists())
    def test_old(self):self.assertFalse(m.authenticate(b'{}',headers(stamp=699),SECRET,1000)['accepted'])
    def test_future(self):self.assertFalse(m.authenticate(b'{}',headers(stamp=1301),SECRET,1000)['accepted'])
    def test_boundary(self):self.assertTrue(m.authenticate(b'{}',headers(stamp=700),SECRET,1000)['accepted'])
    def test_multiple_versions(self):
        h=headers();h['webhook-signature']='v2,unknown v1,bad '+h['webhook-signature'];self.assertTrue(m.authenticate(b'{}',h,SECRET,1000)['accepted'])
    def test_whsec(self):self.assertTrue(m.authenticate(b'{}',headers(),'whsec_'+SECRET,1000)['accepted'])
    def test_raw_utf8_bytes(self):
        payload='é\n'.encode();self.assertTrue(m.authenticate(payload,headers(payload),SECRET,1000)['accepted']);self.assertFalse(m.authenticate(payload.rstrip(),headers(payload),SECRET,1000)['accepted'])
    def test_canonical_stamp(self):
        h=headers();h['webhook-timestamp']='01000'
        with self.assertRaises(ValueError):m.authenticate(b'{}',h,SECRET,1000)
    def test_secret_rejected(self):
        with self.assertRaises(ValueError):m.authenticate(b'{}',headers(),'bad',1000)
    def test_concurrent_processes(self):
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(worker,[self.db]*2)),[False,True])
    def test_expiration_not_early_for_future_stamp(self):
        h=headers(stamp=1200)
        self.assertTrue(m.claim(b'{}',h,SECRET,self.db,1000)['accepted'])
        self.assertFalse(m.claim(b'{}',h,SECRET,self.db,1500)['accepted'])
        h2=headers(stamp=1501)
        self.assertTrue(m.claim(b'{}',h2,SECRET,self.db,1501)['accepted'])
    def test_invalid_does_not_modify(self):
        worker(self.db);before=Path(self.db).read_bytes();m.claim(b'wrong',headers(),SECRET,self.db,1000);self.assertEqual(Path(self.db).read_bytes(),before)


if __name__=='__main__':unittest.main()
