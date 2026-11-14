#!/usr/bin/env python3
"""Validate candidate ArchiMate XML using pinned open-source exchange 3.1 XSD and ArchiMate 3.2 relationship table.
Normative certification requires independent review against the adopted 3.2 specification and official distribution.
"""
import json
import re
from collections import Counter
from pathlib import Path
from urllib.request import urlopen
from xml.etree import ElementTree as ET
from lxml import etree as LET

ROOT=Path(__file__).resolve().parents[1]/"models"/"archimate"
BASE="https://raw.githubusercontent.com/archimatetool/archi/fbfa4474c414477ce88257c956999fb9efdf9e69"
XSD_REPO="org.opengroup.archimate.xmlexchange/xsd"
NS="http://www.opengroup.org/xsd/archimate/3.0/"
XSI="{http://www.w3.org/2001/XMLSchema-instance}type"
RELATION_KEYS={"a":"Access","c":"Composition","f":"Flow","g":"Aggregation","i":"Assignment","n":"Influence","o":"Association","r":"Realization","s":"Specialization","t":"Triggering","v":"Serving"}
D=("baseline","transition","target")
cache=ROOT/".local_archimate_schema"
cache.mkdir(exist_ok=True)
def fetch(url,filename):
    # Always fetch a pinned, inspectable reference rather than silently use unrelated versions.
    content=urlopen(url,timeout=25).read()
    (cache/filename).write_bytes(content)
    return content
for name in ("archimate3_Model.xsd","archimate3_View.xsd","archimate3_Diagram.xsd"):
    fetch(f"{BASE}/{XSD_REPO}/{name}",name)
model_xsd=cache/"archimate3_Model.xsd"
s=model_xsd.read_text()
s=s.replace('schemaLocation="http://www.w3.org/2001/xml.xsd"','schemaLocation="xml.xsd"')
model_xsd.write_text(s)
fetch("https://www.w3.org/2001/xml.xsd","xml.xsd")
legal_raw=fetch(f"{BASE}/com.archimatetool.model/model/relationships.xml","relationships.xml")
matrix=ET.fromstring(legal_raw)
assert matrix.get("version")=="3.2", "Source relation matrix version mismatch"
allow={(s.get("concept"),t.get("concept")):t.get("relations") for s in matrix.findall("source") for t in s.findall("target")}
schema=LET.XMLSchema(LET.parse(str(cache/"archimate3_Diagram.xsd")))
manifest=json.loads((ROOT/"model-population-manifest.candidate.json").read_text())
found={}
for state in D:
    path=ROOT/f"{state}.exchange.xml"
    doc=LET.parse(str(path))
    assert schema.validate(doc), "\n".join(str(x) for x in schema.error_log[:10])
    root=doc.getroot()
    ntag=f"{{{NS}}}"
    elems=root.findall(f"./{ntag}elements/{ntag}element")
    rels=root.findall(f"./{ntag}relationships/{ntag}relationship")
    pd={x.get("identifier") for x in root.findall(f"./{ntag}propertyDefinitions/{ntag}propertyDefinition")}
    ids={}
    for e in elems:
        i=e.get("identifier")
        assert i not in ids, f"{state} duplicate id {i}"
        ids[i]=e.get(XSI)
        assert e.find(f"{ntag}name") is not None
        for prop in e.findall(f"./{ntag}properties/{ntag}property"):
            assert prop.get("propertyDefinitionRef") in pd
    # Rule matrix is independent of XML XSD's syntactic relationship acceptance.
    for rel in rels:
        a,b=rel.get("source"),rel.get("target")
        assert a in ids and b in ids, f"{state} dangling {a} to {b}"
        tp=rel.get(XSI)
        allowed=allow.get((ids[a],ids[b]),"")
        code=next((k for k,v in RELATION_KEYS.items() if v==tp),None)
        assert code and code in allowed, f"{state} invalid ArchiMate 3.2 relation: {ids[a]} {tp} {ids[b]}"
    for view in root.findall(f"./{ntag}views/{ntag}diagrams/{ntag}view"):
        node_ids=set()
        for n in view.findall(f"{ntag}node"):
            assert n.get("elementRef") in ids
            assert n.get("identifier") not in node_ids
            node_ids.add(n.get("identifier"))
        for edge in view.findall(f"{ntag}connection"):
            assert edge.get("source") in node_ids and edge.get("target") in node_ids
            assert any(r.get("identifier")==edge.get("relationshipRef") for r in rels)
    found[state]={"elements":len(elems),"relationships":len(rels),"views":len(root.findall(f"./{ntag}views/{ntag}diagrams/{ntag}view")),"types":dict(Counter(ids.values()))}
    entry=next(x for x in manifest["models"] if x["state"]==state)
    assert found[state]["elements"]==entry["element_count"]
    assert found[state]["relationships"]==entry["relationship_count"]
print(json.dumps({"result":"PASS","format":"ArchiMate Exchange 3.1 XSD with 3.2 relationship matrix","pinned_upstream_commit":"fbfa4474c414477ce88257c956999fb9efdf9e69","models":found,"limitations":["XML format XSD version 3.1; official ArchiMate 3.2 vendor/import interoperability not checked","No assertion all enterprise stakeholders, objects and production systems are inventoried","No authoritative source owner approval or live CRM/Catalyst physical verification"]},indent=2))
