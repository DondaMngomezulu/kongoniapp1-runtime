#!/usr/bin/env python3
"""Synthetic schema checks only; no live CRM or sending permissions."""
import copy
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

root = Path(__file__).resolve().parents[1]
shared = json.loads((root / "shared/governed-object-evidence.candidate.schema.json").read_text())
quote = json.loads((root / "quotations/quotation-covering-email.candidate.schema.json").read_text())
Draft202012Validator.check_schema(shared)
Draft202012Validator.check_schema(quote)
v = Draft202012Validator(shared, format_checker=FormatChecker())
q = Draft202012Validator(quote, format_checker=FormatChecker())

base = {
 "source_record":{"module":"Agreements","id":"123456789"},
 "source_provenance":{"source_ref":"synthetic/source","authority":"CRM","version":"1.0","evidence_status":"VERIFIED"},
 "claims":[{"text":"Example scoped claim","evidence_status":"verified","source_ref":"synthetic/source"}],
 "review_state":"REVIEW_ONLY"
}
assert v.is_valid(base)
families=["Leads","Deals","Accounts","Contacts","Quotes","Quoted_Items","ProductOfferings","ProductOfferingPrices","ProductSpecifications","GroupEntities","FulfilmentEvents","CustomerCommunications","Agreements","Agreement_Templates","Sales_Orders","Purchase_Orders","Invoices","Tenders","TenderRequirements","BusinessDocumentTypes","CustomerDocuments","Products","ServiceOfferings"]
for family in families:
 obj=copy.deepcopy(base);obj["source_record"]["module"]=family;assert v.is_valid(obj),family
assert len(families)==23
bad=copy.deepcopy(base); bad["source_record"]["module"]="MadeUp";assert not v.is_valid(bad)
for key in ("source_record","source_provenance","claims","review_state"):
 bad=copy.deepcopy(base); bad.pop(key);assert not v.is_valid(bad),key
for status,required in (("verified","source_ref"),("proposed","policy_ref"),("clarification_required","clarification_ref"),("not_applicable","applicability_ref")):
 obj=copy.deepcopy(base);obj["claims"]=[{"text":"Test","evidence_status":status}];assert not v.is_valid(obj),(status,"missing evidence")
 obj["claims"][0][required]="synthetic/ref";assert v.is_valid(obj),status
for change in ({"source_record":{"module":"Quotes","id":"no"}},{"review_state":"PUBLISHED"},{"claims":[]},{"extra":"unauthorised"}):
 bad=copy.deepcopy(base);bad.update(change);assert not v.is_valid(bad),change

sections={s:[{"text":"synthetic review claim","evidence_status":"proposed"}] for s in ["requirements","assumptions","technical_offer","finance_offer","commercial_offer","clarifications"]}
pre={"lifecycle_mode":"prequote","source_record":{"module":"Leads","id":"123"},"template":{"template_id":"existing-template","version":"1","merge_schema_id":"MRG-CVR-001","published":False},"sections":sections,"approval_status":"review_only"}
assert q.is_valid(pre)
issued=copy.deepcopy(pre)
issued.update({"lifecycle_mode":"issued_quotation","source_record":{"module":"Quotes","id":"345"},"approval_status":"approved_for_send","parent_document":{"template_id":"parent","document_id":"render","approved":True,"rendered":True},"quote_release":{"quote_id":"345","account_can_issue_quotes":True,"quote_approved":True,"prices_approved":True,"issuer_verified":True}})
issued["template"]["published"]=True
assert q.is_valid(issued)
for key in ["account_can_issue_quotes","quote_approved","prices_approved","issuer_verified"]:
 bad=copy.deepcopy(issued);bad["quote_release"][key]=False;assert not q.is_valid(bad),key
for key in ["approved","rendered"]:
 bad=copy.deepcopy(issued);bad["parent_document"][key]=False;assert not q.is_valid(bad),key
for key in ["quote_release","parent_document"]:
 bad=copy.deepcopy(issued);bad.pop(key);assert not q.is_valid(bad),key
for key in ["requirements","assumptions","technical_offer","finance_offer","commercial_offer","clarifications"]:
 bad=copy.deepcopy(pre);bad["sections"].pop(key);assert not q.is_valid(bad),key
bad=copy.deepcopy(pre);bad["approval_status"]="approved_for_send";assert not q.is_valid(bad)
bad=copy.deepcopy(pre);bad["quote_release"]=issued["quote_release"];assert not q.is_valid(bad)
bad=copy.deepcopy(issued);bad["source_record"]["module"]="Deals";assert not q.is_valid(bad)
print("PASS: 2 draft 2020-12 schemas; 23 CRM object families; evidence-state negative/positive fixtures; 6 sections; prequote/issued gates; 35+ negative fixtures. Synthetic only.")
