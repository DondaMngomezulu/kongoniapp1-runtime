"""Offline UBL 2.5 projection renderer. No CRM or email calls."""
import argparse,json,pathlib
from lxml import etree
ROOT=pathlib.Path(__file__).resolve().parent
INDEX=json.loads((ROOT/"full-template-projection-index.candidate.json").read_text())

def render(doc_type,xml_path,purpose="DOCUMENT",xsd_path=None):
    matches=[x for x in INDEX["profiles"] if x["ubl_type"]==doc_type]
    if len(matches)!=1:raise ValueError("Document type not registered uniquely")
    if purpose not in ("DOCUMENT","EMAIL"):raise ValueError("Unsupported output purpose")
    p=etree.XMLParser(load_dtd=False,no_network=True,resolve_entities=False,huge_tree=False)
    doc=etree.parse(str(xml_path),p)
    if doc.docinfo.doctype:raise ValueError("DOCTYPE forbidden")
    profile=matches[0]
    if doc.getroot().tag!="{"+profile["canonical_xml_root_namespace"]+"}"+doc_type:raise ValueError("Wrong root namespace")
    if xsd_path is None:raise ValueError("Normative UBL 2.5 XSD + imports required before rendering")
    schema=etree.XMLSchema(etree.parse(str(xsd_path),p))
    if not schema.validate(doc):raise ValueError("XSD invalid: "+str(schema.error_log.last_error))
    if profile["send_enabled"]:raise ValueError("Candidate publication invariant violated")
    results=[]
    for key in ("html_path","text_path"):
        xsl=etree.XSLT(etree.parse(str(ROOT/profile[key]),p),access_control=etree.XSLTAccessControl.DENY_ALL)
        results.append(str(xsl(doc,**{"render-purpose":etree.XSLT.strparam(purpose)})))
    return results

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--type",required=True);ap.add_argument("--xml",type=pathlib.Path,required=True);ap.add_argument("--xsd",type=pathlib.Path,required=True)
    ap.add_argument("--purpose",choices=("DOCUMENT","EMAIL"),default="DOCUMENT")
    ap.add_argument("--html",required=True,type=pathlib.Path);ap.add_argument("--text",required=True,type=pathlib.Path)
    args=ap.parse_args();html,text=render(args.type,args.xml,args.purpose,args.xsd)
    args.html.write_text(html,encoding="utf-8");args.text.write_text(text,encoding="utf-8")
    print(json.dumps({"ubl_type":args.type,"purpose":args.purpose,"xsd":"PASS","email_sent":False}))
