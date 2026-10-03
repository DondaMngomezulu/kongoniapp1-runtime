package KongoniZohoCRMArchitecture {
  doc /* SysML v2 textual architecture model. Enterprise meaning remains governed by REG-STD-001 and the governed dictionary. */

  part def GovernedRepository;
  part def ExecutableRepository;
  part def IntegrationRuntime;
  part def OperationalSystem;

  part enterpriseStandards : GovernedRepository;
  part enterpriseDictionary : GovernedRepository;
  part githubModelSource : ExecutableRepository;
  part catalyst : IntegrationRuntime;
  part zohoCRM : OperationalSystem;

  connection governanceFlow connect enterpriseStandards to githubModelSource;
  connection semanticFlow connect enterpriseDictionary to githubModelSource;
  connection deploymentFlow connect githubModelSource to catalyst;
  connection operationFlow connect catalyst to zohoCRM;

  part def CRMCapability {
    attribute capabilityId : String;
    attribute featureGroup : String;
    attribute exposureStatus : String;
  }

  part records : CRMCapability {
    attribute capabilityId = "CAP-CRM-001";
    attribute featureGroup = "Records";
    attribute exposureStatus = "Direct";
  }

  part subforms : CRMCapability {
    attribute capabilityId = "CAP-CRM-031";
    attribute featureGroup = "Records";
    attribute exposureStatus = "Covered via Generic Records";
  }

  part richText : CRMCapability {
    attribute capabilityId = "CAP-CRM-032";
    attribute featureGroup = "Records";
    attribute exposureStatus = "Direct";
  }

  requirement def GovernanceAuthority {
    doc /* Google Drive masters remain semantic/governance authority; executable bindings SHALL NOT redefine governed meaning. */
  }

  requirement def MCPBinding {
    doc /* MCP tools SHALL reference governed capabilities and identifiers and SHALL be treated as implementation bindings. */
  }

  requirement def LifecyclePreservation {
    doc /* Draft/proposed concepts SHALL retain their source lifecycle status and SHALL NOT be promoted by model generation. */
  }
}