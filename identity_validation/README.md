# Identity validation stack (Issue #76)

**Status: DRAFT. Not deployed, not approved for live identities or physical access.**

## Implemented
- SA ID structural plausibility checks (not Home Affairs verification)
- Signed-HMAC document deduplication key
- MIME signature/size intake checks (not malware scanning)
- Abstract OCR and authoritative provider interfaces
- Fail-closed verification decision and onboarding state projection
- Synthetic tests and CI workflow

## Unimplemented mandatory integrations
1. Authenticated intake endpoint, tenant authorisation, content malware scan and encrypted evidence store
2. Tested OCR implementation and SA driver's licence barcode parser
3. Contracted identity verification service with response signature, freshness, consent, correlation and tenant checks
4. Zoho CRM schema/read-write adapter and idempotent update mechanism
5. Signed/versioned terms acceptance records
6. Slot reservation, Thabani's keypad programming confirmation, expiry/usage enforcement and notification delivery evidence
7. POPIA impact assessment, retention policy, security review, independent UAT and release approval

## Guardrails
- Do not place personal ID values, source documents, access PINs or credentials in GitHub.
- No automatic CRM user creation or physical-access activation from structural checks.
- A fake provider returning `evidence_authenticated=True` is **not** trustworthy; the adapter must independently authenticate results.
- `crm_projection` is only a candidate mapping; confirm actual CRM field names and picklist values before writes.
- Reject unknown file signatures and use separate content malware scanning before parsing.
- On any missing evidence or integration failure, retain MANUAL_REVIEW_REQUIRED and do not issue PINs.

## Tests
```sh
python -m unittest discover -s tests -p 'test_identity_*.py' -v
```
