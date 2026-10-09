## GitHub Enterprise Change Route

Refs #ISSUE_NUMBER

Route-ID: ENG-CHANGE-UNIQUE-ID
Task-Class: T2
Change-Class: configuration
Target-System: Name of enterprise system
Target-Environment: development
Authority-Ref: Governed approval / mandate / environment authority record
Verification-Plan: Exact tests, read-back and evidence references
Config-Manifest: governance/configuration-changes/CFG-CHANGE-ID.yaml

### Change, impact and recovery
Explain the intended change and source-of-truth baseline, affected components, potential outage, rollback plan and whether data or production behaviour may change. Do not include credentials, private data, secret values or financial transactions.

### Governance checkpoints
- [ ] GitHub Issue and execution/mandate reference exist
- [ ] Architecture binding and environment authority independently verified
- [ ] Same-change-set change log covers all changed paths
- [ ] Configuration manifest added for any config/low-code/IaC/workflow change
- [ ] CI and negative tests passed
- [ ] Independent PR review and reserved CEO approval, where applicable
- [ ] Production environment / gateway authority verified before deployment
- [ ] GitHub run ID, commit SHA, native platform receipt and CHECK/STUDY evidence recorded
- [ ] ACT decision recorded; DO_COMPLETE does not imply TASK_COMPLETE
