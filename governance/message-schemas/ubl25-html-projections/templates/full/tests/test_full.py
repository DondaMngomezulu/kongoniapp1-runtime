import json,pathlib,unittest,tempfile,sys
from lxml import etree
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from render_full import render,INDEX
class FullSuite(unittest.TestCase):
 def test_exact_profiles(self):
  x=INDEX["profiles"]
  self.assertEqual(len(x),101)
  self.assertEqual(len({p["ubl_type"] for p in x}),101)
  self.assertEqual(len({p["profile_key"] for p in x}),101)
  for p in x:
   self.assertFalse(p["send_enabled"])
   for key in ("html_path","text_path"):
    f=ROOT/p[key];self.assertTrue(f.exists(),str(f))
    etree.XSLT(etree.parse(str(f)))
 def test_strict_gate_before_any_xslt(self):
  with self.assertRaises(ValueError):render("Invoice",ROOT/"fixtures/invoice-preview.xml",xsd_path=None)
 def test_wrong_root_denied(self):
  with tempfile.TemporaryDirectory() as t:
   x=pathlib.Path(t)
   (x/"foreign.xml").write_text('<Order xmlns="urn:oasis:names:specification:ubl:schema:xsd:Order-2"/>')
   with self.assertRaises(ValueError):render("Invoice",x/"foreign.xml",xsd_path=None)
 def test_mismatched_xsd_denied(self):
  with tempfile.TemporaryDirectory() as td:
   t=pathlib.Path(td)
   (t/"sample.xml").write_text('<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"><ID>TEST</ID></Invoice>')
   (t/"different.xsd").write_text('<?xml version="1.0"?><xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" targetNamespace="urn:other" xmlns="urn:other" elementFormDefault="qualified"><xs:element name="Other" type="xs:string"/></xs:schema>')
   with self.assertRaises(ValueError):render("Invoice",t/"sample.xml",xsd_path=t/"different.xsd")
 def test_cover_mode_redacts_fields(self):
  doc=etree.fromstring(b'<Tender xmlns="urn:oasis:names:specification:ubl:schema:xsd:Tender-2"><Details>PRIVATE_SENSITIVE</Details></Tender>')
  for kind in ("html","text"):
   p=next(p for p in INDEX["profiles"] if p["ubl_type"]=="Tender")
   s=etree.XSLT(etree.parse(str(ROOT/p[kind+"_path"])),access_control=etree.XSLTAccessControl.DENY_ALL)
   out=str(s(doc,**{"render-purpose":etree.XSLT.strparam("EMAIL")}))
   self.assertNotIn("PRIVATE_SENSITIVE",out)
   self.assertIn("COVERING",out.upper())
 def test_escape(self):
  doc=etree.fromstring(b'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"><Details>&lt;script&gt;alert(1)&lt;/script&gt;</Details></Invoice>')
  p=next(p for p in INDEX["profiles"] if p["ubl_type"]=="Invoice")
  xslt=etree.XSLT(etree.parse(str(ROOT/p["html_path"])),access_control=etree.XSLTAccessControl.DENY_ALL)
  out=str(xslt(doc))
  self.assertIn("&lt;script&gt;",out);self.assertNotIn("<script>",out)
if __name__=="__main__":unittest.main()
