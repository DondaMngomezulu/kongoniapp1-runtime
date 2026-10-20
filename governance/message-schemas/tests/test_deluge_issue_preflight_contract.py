"""Static candidate contract: a Deluge preflight cannot grant egress authority."""
import unittest
from pathlib import Path

CODE = (Path(__file__).resolve().parents[1] / "controls" / "kng_governed_issue_preflight_v1.review.ds").read_text()

class DelugePreflightContract(unittest.TestCase):
    def test_denies_by_default(self):
        self.assertIn('result.put("release_allowed",false)', CODE)
        self.assertIn('result.put("status","HOLD")', CODE)
        self.assertNotIn('result.put("release_allowed",true)', CODE)
        self.assertNotIn('result.put("status","APPROVED")', CODE)
    def test_no_outbound_or_write(self):
        for forbidden in ("sendmail", "zoho.crm.sendMail", "zoho.crm.updateRecord", "zoho.crm.createRecord", "invokeurl", "zoho.crm.deleteRecord"):
            with self.subTest(operation=forbidden):
                # Compare code statements, not policy comments.
                lines=[line.strip().lower() for line in CODE.splitlines() if line.strip() and not line.strip().startswith("//")]
                self.assertFalse(any(forbidden.lower() in line for line in lines), forbidden)
    def test_requires_existing_records(self):
        for marker in ("CustomerCommunications", "GovernedApprovals", "Governed_Msg_Template_ID",
                       "Template_Version", "Related_Record_ID", "Approval_Evidence", "AI_Payload_Hash",
                       "AUTHORISED_DISPATCH_ADAPTER_NOT_VERIFIED"):
            self.assertIn(marker, CODE)
    def test_no_secrets(self):
        self.assertNotIn("sk-proj-", CODE)
        self.assertNotIn("refresh_token", CODE)
    def test_no_production_publishing_claim(self):
        self.assertIn("NOT A PUBLISHED CRM FUNCTION", CODE)
if __name__ == "__main__":
    unittest.main()
