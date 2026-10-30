# HCP Terraform / TFE publishing

## Decision: monorepo + VCS source directories

This repository is a **module factory monorepo**. Publish each Azure module as its own registry module using HCP Terraform / TFE **VCS-driven modules** with a **subdirectory**:

| Catalog name | Registry address | `source_directory` |
|--------------|------------------|--------------------|
| `azure/naming` | `app.terraform.io/<org>/naming/azurerm` | `modules/azure/naming` |
| `azure/private-endpoint` | `app.terraform.io/<org>/private-endpoint/azurerm` | `modules/azure/private-endpoint` |
| `azure/key-vault` | `app.terraform.io/<org>/key-vault/azurerm` | `modules/azure/key-vault` |
| `azure/storage` | `app.terraform.io/<org>/storage/azurerm` | `modules/azure/storage` |

Provider segment is **`azurerm`** (registry convention), not `azure`.

### Why not one repo per module?

Separate `terraform-azurerm-<name>` repos give independent git tags, but duplicate CI, policy packs, and factory tooling. The factory’s value is shared policies + scaffolding. Monorepo publishing keeps that cohesion; **semver tags can still be per-module** via tag names like `storage/v1.2.0` if your VCS module config supports tag filters, or by accepting shared version bumps across the catalog for v1.

### Catalog fields

- `version` — the published module version (semver string), e.g. `1.0.0`
- `version_constraint` — what consumers should pin, e.g. `~> 1.0`
- `source_directory` — subdirectory registered in TFE
- `tfe_provider` — always `azurerm` for Azure modules

## Setup steps

1. Set `organization` in [`factory/catalog.yaml`](../factory/catalog.yaml).
2. In HCP Terraform → Registry → Modules → **Publish** → VCS → this repo → set subdirectory per module.
3. Tag releases (repo-level or filtered tags per your org standard).
4. Attach the **OPA policy set** from [`policies/opa/`](../policies/opa/) to consuming workspaces.

## CI publish stage

The Azure DevOps pipeline does **not** invent a parallel publish API. With VCS-driven modules, a merge to `main` (and/or a tag) is the publish signal. The pipeline:

1. Validates policies, Terraform, pytest, tflint, Checkov
2. On `main`, verifies catalog metadata and prints registry addresses for operators

If you later choose API publishing, replace that stage with your supported CLI — keep secrets in ADO variable groups.
