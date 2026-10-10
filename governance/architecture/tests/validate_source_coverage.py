#!/usr/bin/env python3
"""Candidate source-architecture checks; not normative ArchiMate XML conformance."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/"models"
def load(n): return json.loads((ROOT/n).read_text(encoding="utf-8"))
src=load("enterprise-source-coverage.candidate.json")
baseline=load("enterprise-baseline.candidate.json")
target=load("enterprise-target.candidate.json")
report=load("enterprise-conformance.candidate.json")
errors=[]
def check(ok,message):
    if not ok:errors.append(message)

concerns={x["source_id"] for x in src["concerns"]}
check(concerns=={f"GOV-{n:02}" for n in range(1,13)},"12 governance areas not fully represented")
vs={x["id"] for x in src["value_streams"]}
check(vs=={f"VS{n:02}" for n in range(0,7)},"Expected VS00 shared and VS01..VS06")
check(len(src["platform_capabilities"])==18,"Platform P01-P18 source inventory incomplete")
check(len(src["application_services"])==48,"Application source snapshot altered")
check(len(src["architecture_requirements"])==15,"Approved EA requirements altered")
check("CONTROLLED_ENGINEERING_DRAFT" in src["metadata"]["lifecycle"],"Draft marker missing")
check(not baseline["conformance"]["architecture_complete"],"Baselines cannot claim completed architecture")
check(target["status"]=="PROPOSED_NOT_APPROVED","Target accidentally marked approved")
check(not report["findings"]["archimate_model_coverage_verified"],"Unvalidated ArchiMate model declared compliant")
check(not report["findings"]["physical_crm_readback_within_this_assessment"],"Unverified CRM readback declared successful")
check(len(report["gaps"])>=6,"Explicit outstanding gaps disappeared")
check(any(x["id"]=="EA-HOLD-01" for x in src["controls_and_holds"]),"Historic VS04/VS06 dispute not held")
check(any(x["id"]=="VS06" and "DRAFT" in x["stage_status"] for x in src["value_streams"]),"VS06 stages prematurely adopted")
check(target["repository_authority"]["business_transactions"]["system"]=="ZOHO_CRM","CRM transaction ownership not preserved")
check(target["repository_authority"]["documents"]["system"]=="GOOGLE_DRIVE","Drive document authority not preserved")
check(target["repository_authority"]["engineering"]["system"]=="GITHUB","Engineering authority not preserved")
check(target["repository_authority"]["runtime"]["system"]=="ZOHO_CATALYST","Catalyst runtime authority not preserved")
for k in ["value_streams","platform_capabilities","application_services","architecture_requirements","architecture_artifacts","reference_processes","crm_module_designs"]:
    ids=[x["id"] for x in src[k] if x.get("id")]
    check(len(ids)==len(set(ids)),f"Duplicate canonical ID in {k}")
for x in src["architecture_artifacts"]:
    for m in x.get("views",[]):
        check(m["domain"] in ("EA-DV-00","EA-DV-01","EA-DV-02","EA-DV-03","EA-DV-04","EA-DV-05"),"Unknown domain")
for x in report["gaps"]:
    check(bool(x.get("owner") and x.get("work_package") and x.get("target")),"Gap has no owner/work package/target")
print(json.dumps({"check":"candidate_ea_source_coverage","result":"FAIL" if errors else "PASS","source_counts":report["source_counts"],"critical_findings_open":len(report["gaps"]),"limitations":["Source census is bounded to selected authoritative registers; not full enterprise population","Not normative ArchiMate 3.2 exchange-schema validation","Not CRM/Catalyst production readback","Not CEO approval"],"errors":errors},indent=2))
raise SystemExit(1 if errors else 0)
