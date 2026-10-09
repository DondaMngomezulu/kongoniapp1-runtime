# Kongoniapp1 Runtime

Cloud-first runtime repository for Kongoniapp1.

This repository is the governed Git source for cloud deployment to Zoho Catalyst.

## Target

| | |
| --- | --- |
| Catalyst organisation | `kongoni` (`931013629`) |
| Catalyst project | `Kongoniapp1` (`86824000000020001`) |
| Development environment | `931013629` |
| Production environment | `10131206251` |
| Development domain | https://kongoniapp1-931013629.development.catalystserverless.com |

The project binding lives in `.catalystrc` and is committed deliberately, so that
every clone deploys to the same project rather than to whichever project a
developer happened to select locally.

## Layout

```
catalyst.json                                  Catalyst CLI configuration
.catalystrc                                    project / environment binding
functions/
  kongoniapp1_health/
    catalyst-config.json                       deployment + execution config
    index.js                                   Basic I/O health probe
    package.json
client/
  client-package.json                          web client manifest
  index.html
  main.css
  main.js
```

`functions.targets` in `catalyst.json` is the list of functions the CLI deploys.
Add a function's directory name there when you add a function.

## Deploying

The Catalyst CLI is not vendored into this repository. Install it and
authenticate once per machine:

```bash
npm install -g zcatalyst-cli
catalyst login
```

Then, from the repository root:

```bash
catalyst deploy                    # deploy to the default (Development) environment
catalyst deploy --only functions   # functions only
catalyst deploy --only client      # web client only
```

To run the runtime locally before deploying:

```bash
catalyst serve
```

## Adding a function

```bash
catalyst functions:add
```

Functions that call Catalyst services (datastore, filestore, cache, auth) need
the Catalyst Node SDK in their own `package.json`:

```bash
npm install zcatalyst-sdk-node
```

The health probe is intentionally dependency-free so that it stays available
even when application dependencies fail to install.

## Runtime stack

Functions are pinned to the `node18` stack in `catalyst-config.json`. Changing
the stack is a one-line edit in that file, per function.


## Enterprise engineering and configuration routing

**CTL-ENG-GH-ROUTE-001** is the adopted group policy requiring a GitHub Issue and reviewed, versioned PR for material systems development and configuration changes. This includes CRM modules/fields/workflows/Blueprints, Catalyst and cloud resources, identity and DNS settings, integrations, low-code tools, AI agent contracts, infrastructure and deployment changes. Routine approved sales/finance/CRM transactions remain in their operational system of record.

Before authoring changes read `AGENTS.md`; use `.github/PULL_REQUEST_TEMPLATE.md`; commit configuration route records under `governance/configuration-changes/` and an auditable change log under `agent-workspace/change-log/`. CI executes `enterprise-route-gate`, `validate-change-log` and agent workspace validation.

**Enforcement status:** the policy is adopted, but branch protection, independent review, environment restrictions and platform-native gateway controls require separate administrative configuration and successful live deployment/read-back tests. A green pull request does not authorise or prove deployment. Never commit access tokens, secrets, personal records or financial transaction data.
