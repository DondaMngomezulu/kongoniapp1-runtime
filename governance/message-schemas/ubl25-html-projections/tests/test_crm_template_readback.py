import json,pathlib,unittest
p=pathlib.Path(__file__).resolve().parents[1]
a=json.loads((p/'crm-template-bindings.candidate.json').read_text())
b=json.loads((p/'manifest.candidate.json').read_text())
class TestCRMReadback(unittest.TestCase):
 def test_types(self):
  self.assertEqual(len(a['profiles']),101)
  self.assertEqual({x['type'] for x in a['profiles']},{x['ubl_type'] for x in b['profiles']})
  self.assertEqual(a['counts']['exact_matches'],27)
  self.assertEqual(a['counts']['types_without_match'],79)
 def test_fail_closed(self):
  self.assertTrue(all(x['issuance']=='DENY' and x['binding_status']=='UNVERIFIED' for x in a['profiles']))
 def test_names(self):
  self.assertEqual(set(a['counts']['unmatched_custom_templates']),{'Tender Response Profile','Equipment Sales Commercial Proposal'})
if __name__=='__main__':unittest.main()
