"use strict";
/** Gate access: CRM tracks approvals; Thabani programs employee PINs on keypad. */
const POLICY=Object.freeze({masterSlot:100,employee:[200,299],visitor:[300,1000],temporaryMaxPasses:10,temporaryExpiresOn:"2026-11-13"});
const inRange=(s,[a,b])=>Number.isInteger(s)&&s>=a&&s<=b;
function classify(slot){return slot===100?"MASTER":inRange(slot,POLICY.employee)?"EMPLOYEE":inRange(slot,POLICY.visitor)?"VISITOR":"INVALID";}
function reconcile({records,controllerSlots=[],inventoryComplete=false}){
 if(!Array.isArray(records)||!Array.isArray(controllerSlots))throw Error("Invalid inventory");
 const issues=[],allocations=[],seen=new Set();
 for(const r of records){
  const reasons=[];
  if(classify(r.slot)!==r.userType)reasons.push("SLOT_TYPE_MISMATCH");
  if(seen.has(r.slot))reasons.push("DUPLICATE_SLOT");
  seen.add(r.slot);
  if(r.userType==="EMPLOYEE"){
   if(r.identityVerified!==true)reasons.push("IDENTITY_NOT_VERIFIED");
   if(r.onboardingApproved!==true)reasons.push("ONBOARDING_NOT_APPROVED");
   if(r.employeeConfirmed!==true)reasons.push("EMPLOYMENT_NOT_CONFIRMED");
   if(r.slotApproved!==true)reasons.push("SLOT_NOT_APPROVED");
   if(r.keypadProgrammedBy!=="Thabani Mkhize"||r.keypadProgrammingConfirmed!==true)reasons.push("KEYPAD_PROGRAMMING_UNCONFIRMED");
  }
  if(r.userType==="VISITOR"){
   if(r.maxPasses!==POLICY.temporaryMaxPasses)reasons.push("TEMPORARY_PASS_LIMIT_MISMATCH");
   if(r.expiresOn!==POLICY.temporaryExpiresOn)reasons.push("TEMPORARY_EXPIRY_MISMATCH");
  }
  if(!inventoryComplete)reasons.push("CONTROLLER_INVENTORY_INCOMPLETE");
  if(!controllerSlots.some(c=>c.slot===r.slot&&c.contactId===r.contactId&&c.programmed===true))reasons.push("CONTROLLER_MAPPING_UNVERIFIED");
  issues.push(...reasons.map(reason=>({contactId:r.contactId,reason})));
  allocations.push({contactId:r.contactId,slot:r.slot,userType:r.userType,status:reasons.length?"PENDING_VERIFICATION":"VERIFIED",accessActive:false});
 }
 return {policy:POLICY,allocations,issues,safeToActivate:false};
}
function onDocumentUploaded(event){
 if(event?.event!=="DOCUMENT_UPLOADED"||!["SA_ID","DRIVERS_LICENCE"].includes(event.documentType))throw Error("Unsupported trigger");
 return {contactId:event.contactId,status:"PENDING_VERIFICATION",accessActive:false};
}
module.exports={POLICY,classify,reconcile,onDocumentUploaded};
