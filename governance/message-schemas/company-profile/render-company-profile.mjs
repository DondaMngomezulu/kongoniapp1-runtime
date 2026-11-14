// WhatsApp company profile candidate renderer. REVIEW_ONLY; never dispatches.
export function renderCompanyProfile(account, spec, { tier = "standard" } = {}) {
  if (!account || !/^\d{10,}$/.test(String(account.id ?? ""))) throw new Error("CRM Account ID required");
  if (!["standard", "extended"].includes(tier) || spec.lifecycle !== "REVIEW_ONLY") throw new Error("Invalid template state or tier");
  const normalise = (v, kind) => {
    if (kind === "lookup_name") return typeof v?.name === "string" ? v.name.trim() : "";
    if (typeof v !== "string" && typeof v !== "number") return "";
    const s = String(v).trim().replace(/[\r\n\t]+/g, " ").replace(/ +/g, " ");
    if (!s || /^(null|undefined|n\/a|not available)$/i.test(s)) return "";
    if (kind === "date" || kind === "year_end") {
      const d = new Date(s + "T12:00:00Z");
      if (!/^\d{4}-\d{2}-\d{2}$/.test(s) || Number.isNaN(d.getTime()) || d.toISOString().slice(0,10) !== s) return "";
      return new Intl.DateTimeFormat("en-GB", {timeZone:"UTC",day:"numeric",month:"long",...(kind === "date" ? {year:"numeric"} : {})}).format(d);
    }
    return s;
  };
  const name = normalise(account.Account_Name, "text");
  const requiredMissing = name ? [] : ["Account_Name"];
  const warnings = [];
  const validated = /^(valid|validated)$/i.test(normalise(account.Master_Data_Status, "text"));
  if (!validated) warnings.push("Master data not validated");
  if (!account.Reg_Address_Source_URL || !account.Reg_Address_As_Of) warnings.push("Registered address provenance incomplete");
  const lines = [`*${name || "COMPANY PROFILE - IDENTITY UNVERIFIED"}*`];
  for (const section of spec.sections) {
    const entries = [];
    for (const field of section.fields) {
      if (field.tier === "extended" && tier === "standard") continue;
      const value = normalise(account[field.key],field.kind);
      if (!value) { if (field.required) requiredMissing.push(field.key); continue; }
      if (field.key === "Account_Name") continue;
      if (field.verification_required && !validated) { warnings.push(field.key + " not verified"); continue; }
      if (field.key === "CSD_Number" && !account.CSD_Registration_Doc) { warnings.push("CSD evidence missing"); continue; }
      if (field.key === "BBBEE_Valid_Until" && !account.BBBEE) { warnings.push("B-BBEE evidence missing"); continue; }
      entries.push(`*${field.label}:* ${value}`);
    }
    if (entries.length) lines.push("",...(section.title ? [`*${section.title}*`] : []),...entries);
  }
  if (requiredMissing.length || warnings.length) lines.push("", "_Draft only. Verify company details before official use._");
  return {message:lines.join("\n"),state:"REVIEW_ONLY",release_eligible:false,crm_account_id:String(account.id),
    missing_required:requiredMissing,warnings,template_key:spec.template_key,template_version:spec.version,channel:spec.channel_code};
}
