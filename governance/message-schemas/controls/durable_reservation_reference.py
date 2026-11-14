"""Durable idempotency reference for AI-NATIVE-ISSUE-SEND-001.

This is an offline SQLite reference model, NOT an authenticated Zoho CRM
outbox, not a transport adapter and not a production deployment. It stores
ONLY opaque digests and outcome markers. The actual CRM implementation must
prove its own atomic unique-create semantics, privilege isolation and
cross-system reconciliation under sandbox load before activating egress.

The model never deletes a reservation automatically, including for UNKNOWN
provider outcomes. A claimed-but-unacknowledged record is permanently
quarantined from automatic replay after a restart.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import re
import sqlite3
from pathlib import Path

HEX64 = re.compile(r"^[0-9a-f]{64}$")
RESERVATION_STATES = {
    "RESERVED", "CLAIMED", "ACKNOWLEDGED", "UNKNOWN", "QUARANTINED"
}

def _valid_digest(s):
    return isinstance(s, str) and HEX64.fullmatch(s) is not None

class DurableReservationReference:
    def __init__(self, filename):
        if not isinstance(filename, (str, Path)) or str(filename) in ("", ":memory:"):
            raise ValueError("FILE_BACKED_DATABASE_REQUIRED")
        self.filename = str(filename)
        self._init()

    @contextmanager
    def _db(self):
        db = sqlite3.connect(self.filename, timeout=15, isolation_level=None)
        try:
            db.execute("PRAGMA busy_timeout=15000")
            db.execute("PRAGMA journal_mode=WAL")
            yield db
        finally:
            db.close()

    def _init(self):
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS dispatch_reservation_reference (
                reservation_key TEXT PRIMARY KEY NOT NULL
                    CHECK(length(reservation_key) = 64),
                instance_sha256 TEXT NOT NULL CHECK(length(instance_sha256) = 64),
                source_revision TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN
                    ('RESERVED', 'CLAIMED', 'ACKNOWLEDGED', 'UNKNOWN', 'QUARANTINED')),
                provider_ref_sha256 TEXT,
                reserved_utc TEXT NOT NULL,
                changed_utc TEXT NOT NULL
            )""")

    @staticmethod
    def _stamp():
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _input(key, digest, revision):
        if not _valid_digest(key) or not _valid_digest(digest) or not isinstance(revision, str) or not revision.strip():
            raise ValueError("INVALID_OPAQUE_RESERVATION")

    def reserve_once(self, key, instance_digest, source_revision):
        """Atomic insert, never UPSERT: a collision must never mutate approval scope."""
        self._input(key, instance_digest, source_revision)
        stamp = self._stamp()
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                db.execute("""INSERT INTO dispatch_reservation_reference
                       (reservation_key, instance_sha256, source_revision, state, reserved_utc, changed_utc)
                       VALUES (?, ?, ?, 'RESERVED', ?, ?)""",
                       (key, instance_digest, source_revision, stamp, stamp))
                db.commit()
                return "RESERVED_REHEARSAL"
            except sqlite3.IntegrityError:
                db.rollback()
                # Do not reveal whether a collision belongs to the same recipient.
                return "DUPLICATE_DENIED"

    def claim(self, key, instance_digest, source_revision):
        """Move exactly one verified reservation to CLAIMED, no provider dispatch."""
        self._input(key, instance_digest, source_revision)
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            changed = db.execute("""UPDATE dispatch_reservation_reference
                SET state='CLAIMED', changed_utc=?
                WHERE reservation_key=? AND instance_sha256=?
                AND source_revision=? AND state='RESERVED'""",
                (self._stamp(), key, instance_digest, source_revision)).rowcount
            db.commit()
            return "CLAIMED_REHEARSAL" if changed == 1 else "CLAIM_DENIED"

    def acknowledge(self, key, provider_reference_digest):
        if not _valid_digest(key) or not _valid_digest(provider_reference_digest):
            raise ValueError("INVALID_DELIVERY_DIGEST")
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            changed = db.execute("""UPDATE dispatch_reservation_reference
                SET state='ACKNOWLEDGED', provider_ref_sha256=?, changed_utc=?
                WHERE reservation_key=? AND state='CLAIMED'""",
                (provider_reference_digest, self._stamp(), key)).rowcount
            db.commit()
            return "ACKNOWLEDGED_REHEARSAL" if changed == 1 else "ACK_DENIED"

    def quarantine(self, key, *, reason_unknown=True):
        if not _valid_digest(key):
            raise ValueError("INVALID_RESERVATION_KEY")
        next_state = "UNKNOWN" if reason_unknown else "QUARANTINED"
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            changed = db.execute("""UPDATE dispatch_reservation_reference
                SET state=?, changed_utc=?
                WHERE reservation_key=? AND state IN ('RESERVED','CLAIMED')""",
                (next_state, self._stamp(), key)).rowcount
            db.commit()
            return next_state + "_REHEARSAL" if changed == 1 else "QUARANTINE_DENIED"

    def read_status(self, key):
        if not _valid_digest(key):
            raise ValueError("INVALID_RESERVATION_KEY")
        with self._db() as db:
            row = db.execute("""SELECT state, instance_sha256, source_revision,
                      provider_ref_sha256 FROM dispatch_reservation_reference
                      WHERE reservation_key=?""", (key,)).fetchone()
        if row is None:
            return None
        return {"state":row[0], "instance_sha256":row[1],
                "source_revision":row[2], "provider_ref_sha256":row[3],
                "production_release_allowed":False}
