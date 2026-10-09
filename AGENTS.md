# AGENTS.md - Kongoni default GitHub workspace

This is the user-selected default connected GitHub repository for Kongoni
enterprise architecture and engineering work **when a mandate does not
explicitly identify another repository**.

1. Read [agent-workspace/governance/default-repository-binding.yaml](agent-workspace/governance/default-repository-binding.yaml) for the machine-readable repository selection and scope.
2. Read and follow [agent-workspace/AGENTS.md](agent-workspace/AGENTS.md), the governing agent collaboration and change-control protocol.
3. Resolve the current active target-architecture state, version, and hash from
   the designated Zoho Catalyst authority before material system changes.
4. Use \`main\` as the working baseline. Inspect relevant feature branches, but do
   not assume proposals or unmerged changes are approved or deployed.
5. For material GitHub mutations, include the mandatory same-change-set change
   log and follow the appropriate authorisation, review, CI and PDCA gates.
6. Respect application and document source-of-truth boundaries. GitHub is for
   generic code, schemas, architecture models, tests and engineering evidence;
   not a replacement for the authoritative records repositories.
7. This GitHub repository is **public**. Never commit secrets, customer data,
   executed agreements, privileged legal advice, live debt information or other
   restricted enterprise records.
8. Explicit user/project selections override the working repository default;
   verify the applicable authority and permissions before changing another repo.

This is an engineering workspace default only. It does not change account-wide
ChatGPT settings, GitHub's default branch, enterprise policy approval, or
production deployment permissions.
