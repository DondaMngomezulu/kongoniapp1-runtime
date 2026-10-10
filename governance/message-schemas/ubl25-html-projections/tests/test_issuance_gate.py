import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from issuance_gate import assess
class NoSend(unittest.TestCase):
 def test_default_deny(self):
  x=assess({"send_enabled":False,"email_policy":"COVERING_EMAIL_ONLY"},{})
  self.assertEqual(x["decision"],"DENY")
  self.assertIn("RENDERED_PARENT_ATTACHMENT_REQUIRED",x["failed_controls"])
  self.assertIn("FORMAL_ORIGINAL_OR_PORTAL_EVIDENCE_MISSING",x["failed_controls"])
 def test_bank_and_port_controls(self):
  x=assess({"send_enabled":False,"email_policy":"EMAIL_PRIMARY"},{"bank_details_included":True,"quote_or_lease_offer_to_lead":True})
  self.assertIn("PROOF_OF_BANKING_MISSING",x["failed_controls"])
  self.assertIn("DURBAN_AVAILABILITY_BLOCK_MISSING",x["failed_controls"])
 def test_no_implicit_approval(self):
  evidence=dict.fromkeys(["canonical_ubl25_xsd_pass","business_rules_pass","parent_document_published","authorised_contracting_entity","crm_issuer_authorised","recipient_verified","no_unresolved_merge_tokens","legal_delivery_channel_approved","audit_retention_authorised","crm_correspondence_readback"],True)
  evidence.update(recipient_opt_out=False,canonical_document_sha256="a"*64,idempotency_key="synthetic-unique")
  profile={"send_enabled":False,"publication":"APPROVED","crm_field_mapping":"APPROVED","email_policy":"EMAIL_PRIMARY"}
  x=assess(profile,evidence);self.assertEqual(x["decision"],"DENY")
  self.assertIn("PROFILE_DISABLED",x["failed_controls"])
if __name__=="__main__":unittest.main()
