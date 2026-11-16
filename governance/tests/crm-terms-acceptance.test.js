"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { crmTermsGate, assessAccessCodeTerms } = require("../crm-terms-acceptance");
const { enterpriseGate, accessGate, onDocumentUploaded, recordVerification } = require("../identity-verification-service");
const { reconcile } = require("../gate-access-allocation-v2");
const NOW = "2030-01-02T12:00:00Z";
const url = id => `https://mail.google.com/mail/u/0/#all/${id}`;
function context() {
  return {
    requiredTermsReference: "SYNTHETIC-TERMS-v1", issuerEmail: "issuer@example.invalid",
    contact: { id: "synthetic-contact", CRM_User_ID: "synthetic-user" },
    crmUser: { id: "synthetic-user", email: "User@example.invalid", status: "active", confirm: true },
    entitlement: { id: "synthetic-entitlement", Contact: { id: "synthetic-contact" },
      Identity_Email: "user@example.invalid", CRM_Terms_Acceptance: "Accepted",
      CRM_Terms_Reference: "SYNTHETIC-TERMS-v1", Evidence_URL: url("aaaaaaaaaaaaaaaa"),
      CRM_Terms_Reply_Evidence: url("bbbbbbbbbbbbbbbb"), CRM_Terms_Accepted_At: "2030-01-02T11:00:00Z" },
    termsRequest: { id: "aaaaaaaaaaaaaaaa", url: url("aaaaaaaaaaaaaaaa"), threadId: "synthetic-thread",
      from: "issuer@example.invalid", to: ["user@example.invalid"], termsReference: "SYNTHETIC-TERMS-v1", sentAt: "2030-01-01T09:00:00Z" },
    reply: { id: "bbbbbbbbbbbbbbbb", url: url("bbbbbbbbbbbbbbbb"), threadId: "synthetic-thread",
      inReplyToMessageId: "aaaaaaaaaaaaaaaa", from: "user@example.invalid", receivedAt: "2030-01-02T10:00:00Z" },
    review: { authorised: true, reviewerId: "synthetic-reviewer", outcome: "Accepted", contactId: "synthetic-contact",
      requestMessageId: "aaaaaaaaaaaaaaaa", replyMessageId: "bbbbbbbbbbbbbbbb",
      termsReference: "SYNTHETIC-TERMS-v1", reviewedAt: "2030-01-02T11:00:00Z" }
  };
}
const separateTerms = { accepted: true, version: "synthetic-v1", acceptedAt: NOW, evidenceRef: "synthetic-evidence" };
function enterprise(c = context()) {
  return enterpriseGate({ crmUser: c.crmUser, identity: { verificationStatus: "VERIFIED", intake: { contactId: c.contact.id } },
    terms: separateTerms, crmTermsContext: c, now: NOW });
}
function access(c = context(), e = enterprise(c)) {
  return accessGate({ enterprise: e, approval: { approved: true, approverId: "synthetic-approver" },
    terms: separateTerms, slot: 250, controller: { slot: 250, programmed: true, programmedBy: "Thabani Mkhize" },
    crmTermsContext: c, now: NOW });
}

test("reviewed explicit reply for the same active user and current terms passes", () => {
  assert.deepEqual(crmTermsGate(context(), NOW), { passed: true, reasons: [] });
  assert.equal(enterprise().passed, true);
  assert.equal(access().issueCredential, true);
});

const denied = [
  ["pending acceptance", c => { c.entitlement.CRM_Terms_Acceptance = "Pending"; }, "CRM_TERMS_NOT_ACCEPTED"],
  ["missing acceptance", c => { delete c.entitlement.CRM_Terms_Acceptance; }, "CRM_TERMS_NOT_ACCEPTED"],
  ["declined acceptance", c => { c.entitlement.CRM_Terms_Acceptance = "Declined"; }, "CRM_TERMS_NOT_ACCEPTED"],
  ["withdrawn acceptance", c => { c.entitlement.CRM_Terms_Acceptance = "Withdrawn"; }, "CRM_TERMS_NOT_ACCEPTED"],
  ["account confirmation is not acceptance", c => { c.entitlement.CRM_Terms_Acceptance = true; }, "CRM_TERMS_NOT_ACCEPTED"],
  ["changed current terms", c => { c.requiredTermsReference = "SYNTHETIC-TERMS-v2"; }, "CRM_TERMS_REFERENCE_MISMATCH"],
  ["missing stored reference", c => { delete c.entitlement.CRM_Terms_Reference; }, "CRM_TERMS_REFERENCE_MISMATCH"],
  ["different request terms", c => { c.termsRequest.termsReference = "other-version"; }, "CRM_TERMS_REFERENCE_MISMATCH"],
  ["missing reply evidence", c => { delete c.entitlement.CRM_Terms_Reply_Evidence; }, "CRM_TERMS_REPLY_UNVERIFIED"],
  ["lookalike evidence host", c => { c.entitlement.CRM_Terms_Reply_Evidence = "https://mail.google.com.evil.invalid/#all/bbbbbbbbbbbbbbbb"; }, "CRM_TERMS_REPLY_UNVERIFIED"],
  ["different reply sender", c => { c.reply.from = "other@example.invalid"; }, "CRM_TERMS_REPLY_UNVERIFIED"],
  ["same thread but not reply to terms request", c => { c.reply.inReplyToMessageId = "cccccccccccccccc"; }, "CRM_TERMS_REPLY_UNVERIFIED"],
  ["different mail thread", c => { c.reply.threadId = "other-thread"; }, "CRM_TERMS_REPLY_UNVERIFIED"],
  ["different reply message", c => { c.reply.id = "cccccccccccccccc"; }, "CRM_TERMS_REPLY_UNVERIFIED"],
  ["request not sent to user", c => { c.termsRequest.to = ["other@example.invalid"]; }, "CRM_TERMS_REQUEST_UNVERIFIED"],
  ["malformed request recipient", c => { c.termsRequest.to = "user@example.invalid"; }, "CRM_TERMS_REQUEST_UNVERIFIED"],
  ["request sender not authorised issuer", c => { c.termsRequest.from = "other@example.invalid"; }, "CRM_TERMS_REQUEST_UNVERIFIED"],
  ["missing current issuer", c => { delete c.issuerEmail; }, "CRM_TERMS_REQUEST_UNVERIFIED"],
  ["different contact", c => { c.entitlement.Contact.id = "other-contact"; }, "CRM_TERMS_SUBJECT_MISMATCH"],
  ["different CRM user", c => { c.contact.CRM_User_ID = "other-user"; }, "CRM_TERMS_SUBJECT_MISMATCH"],
  ["different identity email", c => { c.entitlement.Identity_Email = "other@example.invalid"; }, "CRM_TERMS_SUBJECT_MISMATCH"],
  ["disabled user", c => { c.crmUser.status = "disabled"; }, "CRM_USER_NOT_ACTIVE_CONFIRMED"],
  ["unconfirmed user", c => { c.crmUser.confirm = false; }, "CRM_USER_NOT_ACTIVE_CONFIRMED"],
  ["quoted acceptance without review", c => { c.reply.body = "I accept"; delete c.review; }, "CRM_TERMS_REVIEW_UNVERIFIED"],
  ["question is not acceptance", c => { c.review.outcome = "Question"; }, "CRM_TERMS_REVIEW_UNVERIFIED"],
  ["reviewer not authorised", c => { c.review.authorised = false; }, "CRM_TERMS_REVIEW_UNVERIFIED"],
  ["different review subject", c => { c.review.contactId = "other-contact"; }, "CRM_TERMS_REVIEW_UNVERIFIED"],
  ["different reviewed reply", c => { c.review.replyMessageId = "cccccccccccccccc"; }, "CRM_TERMS_REVIEW_UNVERIFIED"],
  ["missing timestamp", c => { delete c.entitlement.CRM_Terms_Accepted_At; }, "CRM_TERMS_ACCEPTANCE_TIME_INVALID"],
  ["impossible calendar date", c => { c.entitlement.CRM_Terms_Accepted_At = "2030-02-30T11:00:00Z"; }, "CRM_TERMS_ACCEPTANCE_TIME_INVALID"],
  ["future timestamp", c => { c.entitlement.CRM_Terms_Accepted_At = "2031-01-02T11:00:00Z"; }, "CRM_TERMS_ACCEPTANCE_TIME_INVALID"],
  ["reply predates request", c => { c.reply.receivedAt = "2029-01-01T10:00:00Z"; }, "CRM_TERMS_ACCEPTANCE_TIME_INVALID"],
  ["acceptance predates reply", c => { c.entitlement.CRM_Terms_Accepted_At = "2030-01-01T10:00:00Z"; }, "CRM_TERMS_ACCEPTANCE_TIME_INVALID"],
];
for (const [name, change, reason] of denied) test(name, () => {
  const c = context(); change(c);
  const result = crmTermsGate(c, NOW);
  assert.equal(result.passed, false);
  assert.ok(result.reasons.includes(reason), JSON.stringify(result));
  assert.equal(access(c, { passed: true, contactId: "synthetic-contact" }).issueCredential, false);
});

test("legacy booleans cannot bypass CRM reply acceptance", () => {
  assert.equal(enterpriseGate({ crmUser: { status: "active", confirm: true }, identity: { verificationStatus: "VERIFIED" }, terms: separateTerms }).passed, false);
  assert.equal(accessGate({ enterprise: { passed: true }, approval: { approved: true, approverId: "synthetic" }, terms: separateTerms,
    slot: 250, controller: { slot: 250, programmed: true, programmedBy: "Thabani Mkhize" } }).issueCredential, false);
});
test("verified identity for another subject cannot pass enterprise gate", () => {
  const c = context();
  assert.ok(enterpriseGate({ crmUser: c.crmUser, identity: { verificationStatus: "VERIFIED", intake: { contactId: "other-contact" } },
    terms: separateTerms, crmTermsContext: c, now: NOW }).reasons.includes("ENTERPRISE_SUBJECT_MISMATCH"));
});
test("separate enterprise terms and controller gates are preserved", () => {
  const c = context();
  assert.equal(enterpriseGate({ crmUser: c.crmUser, identity: { verificationStatus: "VERIFIED", intake: { contactId: c.contact.id } },
    terms: { accepted: false }, crmTermsContext: c, now: NOW }).passed, false);
  assert.equal(accessGate({ enterprise: enterprise(c), approval: { approved: true, approverId: "synthetic" }, terms: separateTerms,
    slot: 250, controller: { slot: 250, programmed: false }, crmTermsContext: c, now: NOW }).issueCredential, false);
});
test("employee reconciliation holds when email acceptance context is absent", () => {
  const result = reconcile({ records: [{ contactId: "synthetic-contact", slot: 250, userType: "EMPLOYEE", identityVerified: true,
    onboardingApproved: true, employeeConfirmed: true, slotApproved: true, keypadProgrammedBy: "Thabani Mkhize", keypadProgrammingConfirmed: true }],
  controllerSlots: [{ slot: 250, contactId: "synthetic-contact", programmed: true }], inventoryComplete: true });
  assert.equal(result.allocations[0].status, "PENDING_VERIFICATION");
  assert.ok(result.issues.some(issue => issue.reason === "CRM_TERMS_NOT_ACCEPTED"));
  assert.equal(result.safeToActivate, false);
});
test("document upload still cannot verify a person or activate access", () => {
  const intake = onDocumentUploaded({ event: "DOCUMENT_UPLOADED", contactId: "synthetic-contact", documentType: "SA_ID",
    attachmentRef: "synthetic-private-reference", eventId: "synthetic-event" }, Buffer.from("synthetic document"));
  assert.equal(intake.verificationStatus, "PENDING_VERIFICATION");
  assert.equal(intake.accessActive, false);
  assert.throws(() => recordVerification({ intake }, { outcome: "VERIFIED", authorised: false, reviewerId: "synthetic", evidenceRef: "synthetic" }));
});
test("API accepts only an entitlement ID and requires a live evidence adapter", async () => {
  const request = { entitlementId: "synthetic-entitlement" };
  assert.equal((await assessAccessCodeTerms({ ...request, accepted: true }, {})).reasons[0], "INVALID_REQUEST");
  assert.equal((await assessAccessCodeTerms(request, {})).reasons[0], "CRM_TERMS_EVIDENCE_ADAPTER_NOT_CONNECTED");
  assert.equal((await assessAccessCodeTerms(request, { loadTermsContext: async () => { throw Error("private mail content"); } })).reasons[0], "CRM_TERMS_EVIDENCE_UNAVAILABLE");
  const c = context(); c.entitlement.id = "different-entitlement";
  assert.equal((await assessAccessCodeTerms(request, { loadTermsContext: async () => c })).reasons[0], "ENTITLEMENT_MISMATCH");
});
test("API re-reads evidence and never itself issues a credential", async () => {
  const c = context(); let reads = 0;
  const adapter = { loadTermsContext: async () => { reads++; return c; }, now: () => NOW };
  const request = { entitlementId: c.entitlement.id };
  assert.deepEqual(await assessAccessCodeTerms(request, adapter), { status: "TERMS_ACCEPTED", passed: true, reasons: [], issueCredential: false });
  c.entitlement.CRM_Terms_Acceptance = "Withdrawn";
  const result = await assessAccessCodeTerms(request, adapter);
  assert.equal(reads, 2); assert.equal(result.status, "HOLD"); assert.equal(result.issueCredential, false);
  assert.ok(!JSON.stringify(result).includes("example.invalid"));
});
test("native contract keeps issuance disabled and declares all four CRM fields", () => {
  const source = fs.readFileSync(path.join(__dirname, "../crm/gate-access-enrolment-preflight.ds"), "utf8");
  for (const field of ["CRM_Terms_Acceptance", "CRM_Terms_Reference", "CRM_Terms_Reply_Evidence", "CRM_Terms_Accepted_At"])
    assert.ok(source.includes(field));
  assert.ok(source.includes('result.put("schema_version","1.2")'));
  assert.ok(source.includes('result.put("issue_credential",false)'));
  assert.ok(source.includes("HOLD_EVENT_HANDLER_NOT_CONNECTED"));
});
