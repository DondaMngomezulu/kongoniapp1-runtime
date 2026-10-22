import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import {renderCompanyProfile} from './render-company-profile.mjs';

const spec = JSON.parse(readFileSync(new URL('./company-profile.candidate.json',import.meta.url),'utf8'));
const account={
 id:'5643538000008266001',
 Account_Name:'Somkhele Plant (Pty) Ltd',
 Trading_Name:'Somkhele EquipmentCo',
 Company_Registration_Number:'2007/004283/07',
 Tax_Number:'9696029157',
 VAT_Number:'4960258475',
 Registered_Address:'60 Rodio Place, Commercia, Midrand, Gauteng, 1682',
 Business_Physical_Address:'60 Rodio Place, Midrand Industrial Park',
 Company_email:'sales@somkhele.africa',
 Phone:'+27 12 012 6229',
 Organisation_Type:'Private Company',
 Incorporation_Date:'2007-02-09',
 Financial_Year_End:'2027-02-28',
 Parent_Account:{name:'Vector Mining Group',id:'123'},
 Master_Data_Status:'Validated',
 Reg_Address_As_Of:'2026-09-25',
 Reg_Address_Source_URL:'https://example.org/cipc-evidence'
};

test('CRM identity, version and WhatsApp text',()=>{
 const m=renderCompanyProfile(account,spec);
 assert.equal(m.crm_account_id,account.id);
 assert.equal(m.channel,'CH-WHATSAPP');
 assert.equal(m.template_version,'0.1.0');
 assert.match(m.message,/\*Somkhele Plant \(Pty\) Ltd\*/);
 assert.match(m.message,/\*VAT Registration Number:\* 4960258475/);
 assert.ok(!m.message.includes('Parent Company'));
 assert.ok(!m.message.includes('Master_Data_Status'));
 assert.equal(m.release_eligible,false);
});
test('extended view uses lookup name and year-end format',()=>{
 const m=renderCompanyProfile(account,spec,{tier:'extended'});
 assert.match(m.message,/Parent Company:\* Vector Mining Group/);
 assert.match(m.message,/Financial Year-End:\* 28 February/);
 assert.match(m.message,/Incorporation Date:\* 9 February 2007/);
});
test('missing company registration remains a blocking draft',()=>{
 const m=renderCompanyProfile({...account,Company_Registration_Number:null},spec);
 assert.ok(m.missing_required.includes('Company_Registration_Number'));
 assert.match(m.message,/Draft only/);
});
test('master-data verification excludes tax and VAT values',()=>{
 const m=renderCompanyProfile({...account,Master_Data_Status:'PENDING RECONCILIATION'},spec);
 assert.ok(!m.message.includes('9696029157'));
 assert.ok(!m.message.includes('4960258475'));
 assert.equal(m.release_eligible,false);
});
test('optional fields are not emitted as empty',()=>{
 const m=renderCompanyProfile({...account,WhatsApp:null,Website:null},spec);
 assert.ok(!m.message.includes('Website:'));
 assert.ok(!m.message.includes('WhatsApp:'));
});
test('provenance control produces warning when evidence is missing',()=>{
 const m=renderCompanyProfile({...account,Reg_Address_Source_URL:null},spec);
 assert.ok(m.warnings.some(s=>s.includes('provenance')));
});
test('CSD and BBBEE credential fields require evidence',()=>{
 const m=renderCompanyProfile({...account,CSD_Number:'MAAA12345',BBBEE_Valid_Until:'2028-01-01'},spec,{tier:'extended'});
 assert.ok(!m.message.includes('MAAA12345'));
 assert.ok(!m.message.includes('2028-01-01'));
 const m2=renderCompanyProfile({...account,CSD_Number:'MAAA12345',CSD_Registration_Doc:[{id:'crm-evidence'}]},spec,{tier:'extended'});
 assert.ok(m2.message.includes('MAAA12345'));
});
test('reject invalid ID, unknown tier or promoted spec',()=>{
 assert.throws(()=>renderCompanyProfile({...account,id:'fake'},spec));
 assert.throws(()=>renderCompanyProfile(account,spec,{tier:'private'}));
 assert.throws(()=>renderCompanyProfile(account,{...spec,lifecycle:'PRODUCTION'}));
});
test('untrusted newlines are flattened',()=>{
 const m=renderCompanyProfile({...account,Account_Name:'Example\nEntity'},spec);
 assert.match(m.message,/\*Example Entity\*/);
});
