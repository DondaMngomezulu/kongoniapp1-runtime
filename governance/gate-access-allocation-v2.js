"use strict";
/**
 * Gate access allocation v2.  No controller writes or PIN disclosure.
 * Trigger: DOCUMENT_UPLOADED with SA_ID or DRIVERS_LICENCE.
 * Caller supplies verified contact records, controller inventory and approval.
 */
const POLICY = Object.freeze({
  masterSlot: 100,
  employee: [200, 299],
  visitor: [300, 1000],
  visitorMaxUses: 10
});
function inRange(slot, range) {
  return Number.isInteger(slot) && slot >= range[0] && slot <= range[1];
}
function classify(slot) {
  if (slot === POLICY.masterSlot) return "MASTER";
  if (inRange(slot, POLICY.employee)) return "EMPLOYEE";
  if (inRange(slot, POLICY.visitor)) return "VISITOR";
  return "INVALID";
}
function reconcile({records, controllerSlots, uploadedDocument}) {
  if (!uploadedDocument || uploadedDocument.event !== "DOCUMENT_UPLOADED" ||
      !["SA_ID", "DRIVERS_LICENCE"].includes(uploadedDocument.documentType)) {
    throw new Error("Unsupported enrolment trigger");
  }
  const slots = new Set(), pins = new Set(), issues = [], allocations = [];
  for (const r of records) {
    const type = classify(r.slot);
    if (type !== r.userType) issues.push({contactId:r.contactId, reason:"SLOT_TYPE_MISMATCH"});
    if (slots.has(r.slot)) issues.push({contactId:r.contactId, reason:"DUPLICATE_SLOT"});
    slots.add(r.slot);
    if (r.pin != null) {
      if (!/^\\d{4}$/.test(String(r.pin))) issues.push({contactId:r.contactId, reason:"INVALID_PIN"});
      if (pins.has(String(r.pin))) issues.push({contactId:r.contactId, reason:"DUPLICATE_PIN"});
      pins.add(String(r.pin));
    }
    if (!controllerSlots.some(c => c.slot === r.slot && c.contactId === r.contactId)) {
      issues.push({contactId:r.contactId, reason:"CONTROLLER_MAPPING_UNVERIFIED"});
    }
    allocations.push({contactId:r.contactId, slot:r.slot, userType:r.userType,
      status:"PENDING_VERIFICATION", accessActive:false});
  }
  return {policy:POLICY, allocations, issues, safeToActivate:false};
}
module.exports = {POLICY, classify, reconcile};
