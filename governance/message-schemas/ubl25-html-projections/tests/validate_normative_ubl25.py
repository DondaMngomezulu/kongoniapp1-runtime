"""Verify all 101 normative OASIS UBL 2.5 XSDs and their local imports.

- Fetches only the official release xsd/maindoc + xsd/common directories at runtime.
- Never commits or publishes OASIS schema source; emits CI evidence with hashes.
- XMLSchema compilation proves XSD grammar resolution, not document-instance business rules.
"""
import concurrent.futures
import hashlib
import html.parser
import json
import pathlib
import tempfile
import urllib.parse
import urllib.request
from lxml import etree

ROOT=pathlib.Path(__file__).resolve().parents[1]
MANIFEST=json.loads((ROOT/"manifest.candidate.json").read_text(encoding="utf-8"))
BASE="https://docs.oasis-open.org/ubl/os-UBL-2.5/xsd/"
OUT=ROOT/"normative-xsd-assurance.run.json"

class Anchors(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(); self.paths=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":
            href=dict(attrs).get("href")
            if href: self.paths.append(urllib.parse.unquote(href).split("?")[0])

def get(url):
    p=urllib.parse.urlsplit(url)
    if p.scheme!="https" or p.netloc!="docs.oasis-open.org" or not p.path.startswith("/ubl/os-UBL-2.5/xsd/"):
        raise ValueError("Refusing nonnormative or unscoped URL "+url)
    req=urllib.request.Request(url,headers={"User-Agent":"UBL25-governed-XSD-validation/1.0"})
    with urllib.request.urlopen(req,timeout=45) as resp:
        if urllib.parse.urlsplit(resp.geturl()).netloc!="docs.oasis-open.org":
            raise ValueError("Unapproved redirect: "+resp.geturl())
        payload=resp.read(8*1024*1024+1)
    if len(payload)>8*1024*1024:raise ValueError("File exceeds 8MiB guard "+url)
    return payload

def catalog(where):
    v=get(BASE+where+"/")
    h=Anchors();h.feed(v.decode("utf-8"))
    names=[x for x in h.paths if x.endswith(".xsd") and "/" not in x and ".." not in x]
    if len(names)!=len(set(names)):raise AssertionError("Duplicate index entries: "+where)
    return sorted(names)

def check():
    profiles=MANIFEST["profiles"]
    if len(profiles)!=101 or len({p["ubl_type"] for p in profiles})!=101:
        raise AssertionError("Candidate catalogue not 101 unique normative types")
    main_names=catalog("maindoc"); common_names=catalog("common")
    expected=sorted("UBL-"+p["ubl_type"]+"-2.5.xsd" for p in profiles)
    if main_names!=expected:
        raise AssertionError(json.dumps({"missing":sorted(set(expected)-set(main_names)),"extra":sorted(set(main_names)-set(expected))}))
    if len(common_names)<10:
        raise AssertionError("Common XSD library unexpectedly incomplete")
    files=[("maindoc",n) for n in main_names]+[("common",n) for n in common_names]
    hashes={}
    with tempfile.TemporaryDirectory(prefix="oas-ubl25-xsd-") as td:
        work=pathlib.Path(td)
        for d in ("common","maindoc"):(work/d).mkdir()
        def fetch(entry):
            folder,name=entry
            body=get(BASE+folder+"/"+name)
            etree.fromstring(body,etree.XMLParser(no_network=True,resolve_entities=False))
            if not body.lstrip().startswith(b"<?xml"):
                raise ValueError("Non-XML XSD "+name)
            return folder,name,body,hashlib.sha256(body).hexdigest()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            for folder,name,body,digest in pool.map(fetch,files):
                (work/folder/name).write_bytes(body)
                hashes[folder+"/"+name]=digest
        checked=[]
        for prof in profiles:
            name=prof["ubl_type"]
            f=work/"maindoc"/("UBL-"+name+"-2.5.xsd")
            parser=etree.XMLParser(no_network=True,resolve_entities=False)
            doc=etree.parse(str(f),parser)
            namespace="urn:oasis:names:specification:ubl:schema:xsd:"+name+"-2"
            if doc.getroot().attrib.get("targetNamespace")!=namespace:
                raise AssertionError("Unexpected normative namespace "+name)
            etree.XMLSchema(doc) # raises on missing import / invalid XSD
            checked.append(name)
    result={"release":"OASIS-UBL-2.5", "source":BASE,
            "assurance":"NORMATIVE_XSD_INDEX_MATCH_AND_101_SCHEMAS_COMPILE",
            "document_types":len(checked),"common_xsd_files":len(common_names),
            "files_sha256":dict(sorted(hashes.items())),
            "not_proven":["valid business instances","Schematron/business-rule conformance","CRM binding","HTML output","production issuance"]}
    OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="files_sha256"},indent=2))

if __name__=="__main__":check()
