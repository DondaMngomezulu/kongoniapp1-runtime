import json,pathlib,unittest
R=pathlib.Path(__file__).resolve().parents[1]
class CRMFieldBindingTests(unittest.TestCase):
 def test_binding_identity_and_holds(self):
  data=json.loads((R/'crm-field-level-evidence.candidate.json').read_text())
  self.assertEqual(data['covered_document_types'],5)
  self.assertTrue(data['all_tokens_exist'])
  self.assertEqual(len({x['ubl_type'] for x in data['templates']}),5)
  self.assertTrue(all(not x['send_enabled'] for x in data['templates']))
  self.assertTrue(all(all(f['exists'] for f in x['merge_fields']) for x in data['templates']))
  self.assertEqual(data['unverified_template_types'],14)
if __name__=='__main__':unittest.main()
