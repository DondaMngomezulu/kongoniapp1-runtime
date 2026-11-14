"""Offline concurrency and restart tests for a file-backed reference only."""
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "controls"))
from durable_reservation_reference import DurableReservationReference

K="a"*64
D="b"*64
P="c"*64

class DurableReservationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/"outbox.sqlite3"
        self.db=DurableReservationReference(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_one_write_across_instances(self):
        replicas=[DurableReservationReference(self.path) for _ in range(8)]
        with ThreadPoolExecutor(max_workers=12) as pool:
            results=list(pool.map(lambda i: replicas[i%8].reserve_once(K,D,"rev1"),range(40)))
        self.assertEqual(results.count("RESERVED_REHEARSAL"),1)
        self.assertEqual(results.count("DUPLICATE_DENIED"),39)

    def test_restart_never_releases_duplicate(self):
        self.assertEqual(self.db.reserve_once(K,D,"rev1"),"RESERVED_REHEARSAL")
        later=DurableReservationReference(self.path)
        self.assertEqual(later.reserve_once(K,D,"rev1"),"DUPLICATE_DENIED")
        self.assertEqual(later.reserve_once(K,"d"*64,"rev2"),"DUPLICATE_DENIED")

    def test_claim_only_once(self):
        self.db.reserve_once(K,D,"rev1")
        self.assertEqual(self.db.claim(K,D,"rev1"),"CLAIMED_REHEARSAL")
        self.assertEqual(self.db.claim(K,D,"rev1"),"CLAIM_DENIED")
        self.assertEqual(self.db.claim(K,D,"rev2"),"CLAIM_DENIED")

    def test_unknown_outcome_permanently_blocks_retry(self):
        self.db.reserve_once(K,D,"rev1")
        self.db.claim(K,D,"rev1")
        self.assertEqual(self.db.quarantine(K),"UNKNOWN_REHEARSAL")
        restarted=DurableReservationReference(self.path)
        self.assertEqual(restarted.read_status(K)["state"],"UNKNOWN")
        self.assertEqual(restarted.reserve_once(K,D,"rev1"),"DUPLICATE_DENIED")
        self.assertEqual(restarted.acknowledge(K,P),"ACK_DENIED")

    def test_acknowledge_only_claimed(self):
        self.db.reserve_once(K,D,"rev1")
        self.assertEqual(self.db.acknowledge(K,P),"ACK_DENIED")
        self.db.claim(K,D,"rev1")
        self.assertEqual(self.db.acknowledge(K,P),"ACKNOWLEDGED_REHEARSAL")
        self.assertEqual(self.db.acknowledge(K,P),"ACK_DENIED")
        self.assertFalse(self.db.read_status(K)["production_release_allowed"])

    def test_no_plaintext_messages_or_recipients(self):
        self.db.reserve_once(K,D,"rev1")
        raw=self.path.read_bytes()
        self.assertNotIn(b"recipient@example.test",raw)
        self.assertNotIn(b"Synthetic message",raw)

    def test_invalid_reservation_rejected(self):
        with self.assertRaises(ValueError):
            self.db.reserve_once("not-a-hash",D,"rev1")
        with self.assertRaises(ValueError):
            DurableReservationReference(":memory:")

if __name__=="__main__":
    unittest.main()
