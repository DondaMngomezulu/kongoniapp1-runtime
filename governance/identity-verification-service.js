"use strict";
/**
 * Identity verification preflight for gate access.
 * No raw ID images/numbers, PINs, or extracted PII are logged or returned.
 * Extraction is not proof of authenticity. A trusted verification decision is required.
 */
const crypto = require("node:crypto");
const TYPES = Object.freeze(["SA_ID", "DRIVERS_LICENCE"]);
const STATUS = Object.freeze({PENDING:"PENDING_VERIFICATION",REVIEW:"MANUAL_REVIEW",VERIFIED:"VERIFIED",REJECTED:"REJECTED"});
function required(value,name){if(typeof value!=="string"||!value.trim())throw new Error("MISSING_"+name);return value.trim();}
function digest(buffer){if(!Buffer.isBuffer(buffer)||!buffer.length)throw Error("EMPTY_DOCUMENT");return crypto.createHash("sha256").update(buffer).digest("hex");}
function onDocumentUploaded(event, fileBytes){
 if(event?.event!=="DOCUMENT_UPLOADED"||!TYPES.includes(event.documentType))throw Error("UNSUPPORTED_DOCUMENT");
 const contactId=required(event.contactId,"CONTACT_ID");
 const attachmentRef=required(event.attachmentRef,"ATTACHMENT_REF");
 const sha256=digest(fileBytes);
 return {eventId:required(event.eventId,"EVENT_ID"),contactId,documentType:event.documentType,
  attachmentRef,sha256,idempotencyKey:crypto.createHash("sha256").update(contactId+"|"+event.documentType+"|"+sha256).digest("hex"),
  verificationStatus:STATUS.PENDING,accessActive:false};
}
/** Adapter must securely return extracted fields + per-field confidence. Never persist raw extracted PII to logs. */
async function extractDocument(intake, extractor){
 if(typeof extractor!=="function")throw Error("EXTRACTOR_NOT_CONFIGURED");
 const result=await extractor({attachmentRef:intake.attachmentRef,documentType:intake.documentType});
 if(!result||typeof result!=="object"||!result.fields||!result.confidence)throw Error("INVALID_EXTRACTION");
 return {intake,extraction:result,verificationStatus:STATUS.REVIEW,accessActive:false};
}
/** Verification must be an authenticated, separately authorised manual or provider decision. */
function recordVerification(state,decision){
 if(!["VERIFIED","REJECTED"].includes(decision?.outcome))throw Error("INVALID_DECISION");
 required(decision.reviewerId,"REVIEWER_ID");required(decision.evidenceRef,"EVIDENCE_REF");
 if(decision.authorised!==true||decision.identityMatched!==true&&decision.outcome==="VERIFIED")throw Error("UNAUTHORISED_VERIFICATION");
 return {intake:state.intake,verificationStatus:decision.outcome,reviewerId:decision.reviewerId,
  evidenceRef:decision.evidenceRef,verifiedAt:required(decision.timestamp,"TIMESTAMP"),accessActive:false};
}
function enterpriseGate({crmUser,identity,terms}){
 const reasons=[];
 if(!crmUser||crmUser.status!=="active"||crmUser.confirm!==true)reasons.push("CRM_USER_NOT_ACTIVE_CONFIRMED");
 if(identity?.verificationStatus!=="VERIFIED")reasons.push("IDENTITY_NOT_VERIFIED");
 if(terms?.accepted!==true||!terms.version||!terms.acceptedAt||!terms.evidenceRef)reasons.push("ENTERPRISE_TERMS_NOT_ACCEPTED");
 return {passed:reasons.length===0,reasons};
}
function accessGate({enterprise,approval,terms,slot,controller}){
 const reasons=[];
 if(enterprise?.passed!==true)reasons.push("ENTERPRISE_GATE_INCOMPLETE");
 if(approval?.approved!==true||!approval.approverId)reasons.push("ACCESS_NOT_APPROVED");
 if(terms?.accepted!==true||!terms.version||!terms.acceptedAt||!terms.evidenceRef)reasons.push("ACCESS_TERMS_NOT_ACCEPTED");
 if(!Number.isInteger(slot)||slot<200||slot>299)reasons.push("INVALID_EMPLOYEE_SLOT");
 if(controller?.slot!==slot||controller?.programmed!==true||controller?.programmedBy!=="Thabani Mkhize")reasons.push("CONTROLLER_NOT_CONFIRMED");
 return {passed:reasons.length===0,reasons,issueCredential:reasons.length===0};
}
module.exports={TYPES,STATUS,onDocumentUploaded,extractDocument,recordVerification,enterpriseGate,accessGate};
