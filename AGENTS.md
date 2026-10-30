# AGENTS.md — Terraform Module Factory

Instructions for coding agents working in this repository. Humans can follow them too; agents **must**.

## Mission

Help platform engineers produce Terraform modules that meet this platform’s **policy pack**: secure baselines, naming standards, required tags, and **Private Link / Private Endpoint over public access**. Azure is primary; AWS/GCP share layout and schema only until real modules exist.

## Non-negotiables

1. **Policy is source of truth.** Behavior changes that affect security, naming, tags, or networking start in [`policies/`](policies/) (and JSON Schema), then modules, Checkov, OPA data, and templates stay aligned.
2. **Private connectivity first.** Do not introduce public network access as a default. Network ACLs / IP allowlists are **defense-in-depth only**, never a substitute for Private Endpoint / Private Link.
3. **Break-glass stays loud.** Any public-access escape hatch must be an explicit variable named like `allow_public_network_access` (default `false`).
4. **Required tags** come from [`policies/tags.required.yaml`](policies/tags.required.yaml) via `tf-factory` / `policy_engine.required_tags` — do not hardcode a divergent list.
5. **Compose catalog modules.** Prefer `azure/naming` and `azure/private-endpoint` over re-implementing naming or PE inline.
6. **No secrets in git.**
7. **Naming has one generator.** Edit the NamingStandard policy, then run `tf-factory generate-naming`. Never hand-edit generated files under `modules/azure/naming/` (except README prose if needed). Truncation **preserves suffix**; never leave a trailing `-`.
8. **Plan-time enforcement is OPA (or Sentinel).** Checkov guards defaults in CI; TFE workspaces must attach [`policies/opa/`](policies/opa/). Regenerate data with `tf-factory export-policy-data`.

## Repo map

| Path | Role |
|------|------|
| [`policies/`](policies/) | YAML/JSON requirements + schema |
| [`policies/opa/`](policies/opa/) | OPA Rego + exported `data/policy_pack.json` for TFE |
| [`factory/`](factory/) | Python `tf-factory` CLI, [`catalog.yaml`](factory/catalog.yaml), Jinja2 scaffolds |
| [`modules/azure/`](modules/azure/) | `naming` (generated), `private-endpoint`, `key-vault`, `storage` |
| [`docs/TFE_PUBLISHING.md`](docs/TFE_PUBLISHING.md) | Monorepo + VCS source-directory publishing |
| [`checkov/custom_checks/`](checkov/custom_checks/) | Default/static Checkov checks (not a substitute for OPA) |
| [`examples/`](examples/) | Composed examples (`storage_use_azuread = true`) |
| [`pipelines/azure-devops/`](pipelines/azure-devops/) | CI: policy sync, pytest, tflint, validate, terraform test, Checkov |

## How to work

### Naming changes

```bash
# edit policies/naming.example.yaml (or naming.yaml)
tf-factory generate-naming --policies ./policies
tf-factory render-name --type key_vault --workload claimsprocessing --env prod --region eastus2 --suffix 01
cd factory && pytest -q
cd ../modules/azure/naming && terraform test
```

### Scaffold a new module

```bash
tf-factory scaffold --cloud azure --name <module> --from-policy ./policies
# Catalog required_inputs are wired so terraform validate succeeds.
# Register the module in factory/catalog.yaml before publishing.
```

### Policy / enforcement changes

1. Edit YAML under `policies/`.
2. `tf-factory validate-policy && tf-factory export-policy-data`
3. Update OPA Rego if a new rule class is needed.
4. Add Checkov only for default-safety mirrors — do not duplicate OPA as the sole control.
5. Prefer OPA `attribute_rules` fed from YAML `require` / `deny` blocks.

### Provider / Azure

- Pin **`azurerm ~> 4.0`**. Use `rbac_authorization_enabled` (not `enable_rbac_authorization`).
- When `shared_access_key_enabled = false`, consumer providers **must** set `storage_use_azuread = true`.
- Applying Private Link modules requires a runner that can reach the private endpoint.

## Verification

```bash
tf-factory validate-policy --policies ./policies
tf-factory generate-naming --policies ./policies
tf-factory export-policy-data --policies ./policies
cd factory && pytest -q && cd ..
terraform fmt -check -recursive modules examples
(cd modules/azure/naming && terraform init -backend=false && terraform test)
for d in modules/azure/*/; do (cd "$d" && terraform init -backend=false && terraform validate); done
checkov -d modules -d examples --config-file .checkov.yaml --framework terraform
```

## Publishing (TFE)

**Chosen model:** monorepo + HCP/TFE VCS modules with `source_directory` per catalog entry. Provider segment is **`azurerm`**. See [`docs/TFE_PUBLISHING.md`](docs/TFE_PUBLISHING.md).

- `version` = published semver
- `version_constraint` = consumer pin (`~> 1.0`)

## Do not

- Chop names from the end (drops suffix / causes collisions).
- Hand-edit generated naming module locals.
- Treat Checkov alone as plan-time enforcement for TFE consumers.
- Default `public_network_access_enabled = true`.
- Use `tfe_provider: azure` — use `azurerm`.
- Commit secrets or real subscription IDs.
