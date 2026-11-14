import json,pathlib,unittest
p=pathlib.Path(__file__).parents[1]
a=json.loads((p/'manifest.candidate.json').read_text())
s=json.loads((p/'manifest.schema.json').read_text())
class ProjectionContract(unittest.TestCase):
 def test_shape(self):
  from jsonschema import Draft202012Validator
  Draft202012Validator.check_schema(s)
  Draft202012Validator(s).validate(a)
 def test_cardinality(self):
  x=a['profiles'];self.assertEqual(len(x),101)
  self.assertEqual(len(set(y['ubl_type'] for y in x)),101)
  self.assertEqual(len(set(y['projection_key'] for y in x)),101)
  self.assertEqual(sum(bool(y['legacy_type_id']) for y in x),93)
  self.assertEqual(sum(not y['legacy_type_id'] for y in x),8)
  self.assertEqual(set(y['email_policy'] for y in x),{'EMAIL_PRIMARY','EMAIL_WITH_CANONICAL_DOCUMENT','COVERING_EMAIL_ONLY'})
 def test_release_blocked(self):
  for t in a['profiles']:
   self.assertFalse(t['approved_to_send']);self.assertTrue(t['hold']);self.assertIsNone(t['html_template_id'])
   self.assertEqual(t['normative_xsd_uri'],'https://docs.oasis-open.org/ubl/os-UBL-2.5/xsd/maindoc/UBL-'+t['ubl_type']+'-2.5.xsd')
 def test_new_types(self):
  new={t['ubl_type'] for t in a['profiles'] if not t['legacy_type_id']}
  self.assertEqual(new,{'DeliveryNote','InvoiceStatusRequest','InvoiceStatusResponse','ProcurementStatus','ProcurementStatusRequest','WasteMovement','WasteNotification','WorkReport'})
 def test_sensitive_types_not_email_primary(self):
  for t in a['profiles']:
   if t['ubl_type'] in {'Invoice','TenderContract','DigitalAgreement','CertificateOfOrigin','WasteMovement'}:self.assertNotEqual(t['email_policy'],'EMAIL_PRIMARY')
if __name__=='__main__':unittest.main()
