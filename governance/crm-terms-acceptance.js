"use strict";

// Pure assessment over server-fetched evidence. Client assertions are not evidence.
const text = value => typeof value === "string" && value.trim().length > 0;
const email = value => text(value) ? value.trim().toLowerCase() : "";
function instant(value) {
  if (!text(value) || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(value)) return NaN;
  const [year, month, day, hour, minute, second] = value.slice(0, 19).split(/\D/).map(Number);
  const calendar = new Date(Date.UTC(year, month - 1, day, hour, minute, second));
  if (!Number.isFinite(calendar.getTime()) || calendar.toISOString().slice(0, 19) !== value.slice(0, 19)) return NaN;
  return Date.parse(value);
}
function messageId(url) {
  if (!text(url)) return null;
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== "https:" || parsed.hostname !== "mail.google.com" || parsed.username || parsed.password || parsed.port) return null;
    return /^#(?:all|inbox|sent)\/([a-f0-9]+)$/i.exec(parsed.hash)?.[1] || null;
  } catch { return null; }
}

/**
 * Context must come from an authenticated CRM/mail evidence adapter, not HTTP JSON.
 * The adapter normalises In-Reply-To to the provider request message ID and loads
 * the explicit human review; this module never infers consent from email text.
 */
function crmTermsGate(context = {}, now = new Date().toISOString()) {
  const { entitlement: e, contact, crmUser: user, termsRequest: request,
    reply, review, requiredTermsReference, issuerEmail } = context || {};
  const reasons = [];
  if (!user || user.status !== "active" || user.confirm !== true) reasons.push("CRM_USER_NOT_ACTIVE_CONFIRMED");
  if (!text(contact?.id) || !text(user?.id) || contact.CRM_User_ID !== user.id || e?.Contact?.id !== contact.id ||
      !email(user?.email) || email(e?.Identity_Email) !== email(user.email)) reasons.push("CRM_TERMS_SUBJECT_MISMATCH");
  if (e?.CRM_Terms_Acceptance !== "Accepted") reasons.push("CRM_TERMS_NOT_ACCEPTED");
  if (!text(requiredTermsReference) || e?.CRM_Terms_Reference !== requiredTermsReference ||
      request?.termsReference !== requiredTermsReference) reasons.push("CRM_TERMS_REFERENCE_MISMATCH");
  if (!text(request?.id) || messageId(e?.Evidence_URL) !== request.id || messageId(request?.url) !== request.id ||
      !email(issuerEmail) || email(request?.from) !== email(issuerEmail) || !Array.isArray(request?.to) ||
      !request.to.some(address => email(address) === email(user?.email))) reasons.push("CRM_TERMS_REQUEST_UNVERIFIED");
  if (!text(reply?.id) || messageId(e?.CRM_Terms_Reply_Evidence) !== reply.id || messageId(reply?.url) !== reply.id ||
      email(reply?.from) !== email(user?.email) || !email(reply?.from) ||
      !text(request?.threadId) || reply?.threadId !== request.threadId || reply?.inReplyToMessageId !== request?.id)
    reasons.push("CRM_TERMS_REPLY_UNVERIFIED");
  if (review?.authorised !== true || review?.outcome !== "Accepted" || !text(review?.reviewerId) ||
      review?.contactId !== contact?.id || review?.replyMessageId !== reply?.id ||
      review?.requestMessageId !== request?.id || review?.termsReference !== requiredTermsReference)
    reasons.push("CRM_TERMS_REVIEW_UNVERIFIED");
  const sent = instant(request?.sentAt), received = instant(reply?.receivedAt),
    accepted = instant(e?.CRM_Terms_Accepted_At), reviewed = instant(review?.reviewedAt), current = instant(now);
  if (![sent, received, accepted, reviewed, current].every(Number.isFinite) ||
      sent > received || received > accepted || accepted !== reviewed || accepted > current)
    reasons.push("CRM_TERMS_ACCEPTANCE_TIME_INVALID");
  return { passed: reasons.length === 0, reasons };
}

/** No issuance side effects. A missing live evidence adapter always returns HOLD. */
async function assessAccessCodeTerms(request, adapters) {
  if (!request || Object.keys(request).some(key => key !== "entitlementId") || !text(request.entitlementId))
    return { status: "HOLD", passed: false, reasons: ["INVALID_REQUEST"], issueCredential: false };
  if (typeof adapters?.loadTermsContext !== "function")
    return { status: "HOLD", passed: false, reasons: ["CRM_TERMS_EVIDENCE_ADAPTER_NOT_CONNECTED"], issueCredential: false };
  try {
    const context = await adapters.loadTermsContext(request.entitlementId);
    if (context?.entitlement?.id !== request.entitlementId)
      return { status: "HOLD", passed: false, reasons: ["ENTITLEMENT_MISMATCH"], issueCredential: false };
    const gate = crmTermsGate(context, adapters.now?.() || new Date().toISOString());
    return { status: gate.passed ? "TERMS_ACCEPTED" : "HOLD", ...gate, issueCredential: false };
  } catch {
    return { status: "HOLD", passed: false, reasons: ["CRM_TERMS_EVIDENCE_UNAVAILABLE"], issueCredential: false };
  }
}

module.exports = { crmTermsGate, assessAccessCodeTerms };
