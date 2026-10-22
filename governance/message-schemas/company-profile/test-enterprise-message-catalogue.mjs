import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
const catalog = JSON.parse(readFileSync(new URL("./enterprise-message-catalogue.candidate.json",import.meta.url),"utf8"));
const expectedModules = new Set(["Leads","Deals","Quotes","Tenders","CustomerServiceRequests","CustomerDocuments","DeliveryEvents","CustomerCommunications"]);
test("all candidate profiles unique and tied to existing native CRM templates",()=>{
 assert.equal(catalog.templates.length,19);
 assert.equal(new Set(catalog.templates.map(x=>x.key)).size,19);
 assert.equal(new Set(catalog.templates.map(x=>x.crm_template_id)).size,19);
 for(const t of catalog.templates){ assert.match(t.crm_template_id,/^\d{16,}$/);assert.equal(t.status,"REVIEW_ONLY"); assert.equal(t.transmission,"DISABLED");}
});
test("enterprise standards and exact CRM module-field bindings declared",()=>{
 for(const t of catalog.templates){
  assert.ok(t.semantic_authority.length>0);
  assert.ok(expectedModules.has(t.primary_source.module));
  assert.ok(t.bindings.length>=2);
  for(const b of t.bindings){assert.equal(b.crm_module,t.primary_source.module);assert.ok(b.crm_field);assert.equal(b.verified_in_live_metadata,true);}
 }
});
test("no unapproved message automatically sent",()=>{
 assert.equal(catalog.lifecycle,"REVIEW_ONLY");assert.equal(catalog.rules.sending,"DISABLED");assert.equal(catalog.canonical_catalogue_id,null);
});
test("preserves existing governed crosswalk and source register",()=>{
 assert.match(catalog.authority_register,/1TlHa9Q43Y/);
 assert.ok(catalog.templates.some(t=>t.enterprise_source_binding==="VS02-01"));
 assert.ok(catalog.templates.some(t=>t.crm_template_id==="5643538000009329003"));
});
