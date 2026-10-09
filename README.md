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

## Default engineering repository

The user-selected **default connected GitHub repository** for Kongoni enterprise
architecture, governed schemas, document/form engineering contracts, integrations,
agent collaboration, source code, and technical change management is
[DondaMngomezulu/kongoniapp1-runtime](https://github.com/DondaMngomezulu/kongoniapp1-runtime),
using \`main\` as the default baseline for reading. Explicit project instructions
or an approved project-specific repository binding take precedence.

Machine-readable selection: [agent-workspace/governance/default-repository-binding.yaml](agent-workspace/governance/default-repository-binding.yaml).
Agent entrypoint: [AGENTS.md](AGENTS.md) and [agent-workspace/AGENTS.md](agent-workspace/AGENTS.md).

This selection does not change GitHub's default branch or the authoritative
systems for business records: the relevant approved records repository/Google
Drive, Zoho CRM, Zoho Books and Zoho Catalyst retain their designated roles.
Proposed architecture branches and models are not approved by repository
selection. This repository is public; never commit customer data, signed
agreements, credentials or restricted records.
