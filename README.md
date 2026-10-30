# Terraform Module Factory

Platform engineering toolkit for building Terraform modules that meet **secure baselines**, **naming standards**, and **Private Link–first networking**. Azure is the primary target; AWS and GCP share the same layout and policy schema.

## What you get

| Area | Contents |
|------|----------|
| **Policy pack** | YAML/JSON requirements under [`policies/`](policies/) (naming, security, private networking, tags) |
| **Factory CLI** | Python `tf-factory` — validate policies, scaffold modules, render names, list catalog |
| **Azure catalog** | `naming`, `private-endpoint`, `key-vault`, `storage` — private by default |
| **Checkov** | Custom checks mirroring the policy pack |
| **Azure DevOps** | CI template for fmt / validate / Checkov / TFE publish guidance |

**Networking stance:** Private Endpoints / Private Link are required. Network ACLs are defense-in-depth only — never the primary exposure control.

## Repository layout

```text
policies/           Platform requirements + JSON Schema
factory/            Python CLI, catalog.yaml, Jinja2 templates
modules/azure/      Starter modules (naming, PE, Key Vault, Storage)
modules/aws|gcp/    Placeholders for future clouds
examples/           Composed private storage example
checkov/            Custom Checkov checks
pipelines/          Azure DevOps module CI
```

## Quick start

### 1. Install the factory

```bash
cd factory
python3 -m pip install -e .
cd ..
```

### 2. Validate policies

```bash
tf-factory validate-policy --policies ./policies
```

### 3. Render a name (example naming standard)

```bash
tf-factory render-name \
  --type storage_account \
  --workload payments \
  --env prod \
  --region eastus \
  --suffix 01
```

Replace [`policies/naming.example.yaml`](policies/naming.example.yaml) with your real naming standards (keep `apiVersion` / `kind`).

### 4. List catalog modules

```bash
tf-factory list-modules
```

### 5. Scaffold a new Azure module

```bash
tf-factory scaffold --cloud azure --name redis --from-policy ./policies
```

The scaffold injects secure defaults (`allow_public_network_access = false`), required-tag validation, and `module` blocks for policy-required references (`azure/naming`, `azure/private-endpoint`).

### 6. Run Checkov locally

```bash
pip install checkov
checkov -d modules -d examples --config-file .checkov.yaml --framework terraform
```

## Using catalog modules

### Local development

```hcl
module "naming" {
  source      = "../../modules/azure/naming"
  workload    = "payments"
  environment = "prod"
  region      = "eastus"
}

module "storage" {
  source                      = "../../modules/azure/storage"
  name                        = module.naming.storage_account
  resource_group_name         = var.resource_group_name
  location                    = var.location
  private_endpoint_subnet_id  = var.pe_subnet_id
  tags                        = var.tags
}
```

See [`examples/azure-storage-private/`](examples/azure-storage-private/).

### Terraform Enterprise (TFE / HCP Terraform)

1. Set your organization in [`factory/catalog.yaml`](factory/catalog.yaml) (`organization: your-org`).
2. Publish modules via VCS connection (recommended) or your publish workflow.
3. Consume from the private registry:

```hcl
module "storage" {
  source  = "app.terraform.io/<org>/storage/azure"
  version = "~> 1.0"
  # ...
}
```

Scaffold with TFE sources:

```bash
tf-factory scaffold --cloud azure --name redis --from-policy ./policies --use-tfe
```

## Azure DevOps

Import [`pipelines/azure-devops/module-ci.yml`](pipelines/azure-devops/module-ci.yml).

- Runs policy validation, `terraform fmt` / `validate`, and Checkov on PRs and `main`.
- Optional publish stage expects secret variables `TFE_TOKEN` / `TFE_ORG` (never commit tokens).

## Secure baseline (Azure v1)

| Module | Highlights |
|--------|------------|
| **naming** | Policy-aligned helpers; no resources |
| **private-endpoint** | PE + optional Private DNS zone group |
| **key-vault** | Public access off, RBAC, soft delete, purge protection, composed PE |
| **storage** | Public access off, TLS 1.2+, no public blobs, Deny ACLs, composed PE |

Break-glass public access uses the loudly named variable `allow_public_network_access` — custom Checkov checks fail when it is `true`.

## Multi-cloud

- Policy files accept `cloud: azure | aws | gcp | multi`.
- AWS/GCP folders are stubs; copy `factory/templates/azure/module` when you add those clouds.

## Policy authoring

All policy files must match [`policies/schema/policy.schema.json`](policies/schema/policy.schema.json). Kinds:

- `NamingStandard`
- `SecurityBaseline`
- `NetworkingPrivate`
- `TagsRequired`

YAML or JSON both work.
