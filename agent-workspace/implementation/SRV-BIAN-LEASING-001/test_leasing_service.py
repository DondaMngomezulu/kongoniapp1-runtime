import unittest
from leasing_service import initiate, retrieve, update, LeasingError


class LeasingServiceTests(unittest.TestCase):
    def payload(self):
        return {
            "customer_ref": "CRM-TEST-001",
            "asset_refs": ["ASSET-TEST-001"],
            "currency": "ZAR",
            "effective_date": "2026-09-01",
            "maturity_date": "2029-08-31",
            "correlation_id": "TEST-CORR-001",
            "idempotency_key": "TEST-IDEMP-001",
        }

    def test_initiate(self):
        record = initiate(self.payload())
        self.assertEqual(record["customer_ref"], "CRM-TEST-001")
        self.assertEqual(record["facility_status"], "INITIATED")

    def test_retrieve(self):
        record = initiate(self.payload())
        store = {record["leasing_id"]: record}
        self.assertEqual(retrieve(store, record["leasing_id"])["leasing_id"], record["leasing_id"])

    def test_update(self):
        record = initiate(self.payload())
        store = {record["leasing_id"]: record}
        changed = update(store, record["leasing_id"], {"facility_status": "ACTIVE"})
        self.assertEqual(changed["facility_status"], "ACTIVE")

    def test_reject_invalid_dates(self):
        payload = self.payload()
        payload["maturity_date"] = "2026-08-01"
        with self.assertRaises(LeasingError):
            initiate(payload)

    def test_reject_immutable_update(self):
        record = initiate(self.payload())
        store = {record["leasing_id"]: record}
        with self.assertRaises(LeasingError):
            update(store, record["leasing_id"], {"customer_ref": "CRM-OTHER"})


if __name__ == "__main__":
    unittest.main()
