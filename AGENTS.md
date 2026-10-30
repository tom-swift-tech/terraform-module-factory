# AGENTS.md — Terraform Module Factory

Instructions for coding agents working in this repository. Humans can follow them too; agents **must**.

## Mission

Help platform engineers produce Terraform modules that meet this platform’s **policy pack**: secure baselines, naming standards, required tags, and **Private Link / Private Endpoint over public access**. Azure is primary; AWS/GCP share layout and schema only until real modules exist.

## Non-negotiables

1. **Policy is source of truth.** Behavior changes that affect security, naming, tags, or networking start in [`policies/`](policies/) (and JSON Schema), then modules, Checkov, and templates stay aligned.
2. **Private connectivity first.** Do not introduce public network access as a default. Network ACLs / IP allowlists are **defense-in-depth only**, never a substitute for Private Endpoint / Private Link.
3. **Break-glass stays loud.** Any public-access escape hatch must be an explicit variable named like `allow_public_network_access` (default `false`). Do not hide public enablement behind vague flags.
4. **Required tags.** Resources and module `tags` variables must enforce: `Environment`, `Owner`, `CostCenter`, `DataClassification` (see [`policies/tags.required.yaml`](policies/tags.required.yaml)).
5. **Compose catalog modules.** Prefer `azure/naming` and `azure/private-endpoint` (and other catalog entries) over re-implementing naming or PE inline.
6. **No secrets in git.** Tokens, service principals, TFE credentials, and real subscription IDs stay out of the repo. Examples may use obvious placeholders.
7. **Do not invent proprietary naming.** Replace or extend [`policies/naming.example.yaml`](policies/naming.example.yaml); keep `apiVersion: tf-factory/v1` and `kind: NamingStandard`.

## Repo map

| Path | Role |
|------|------|
| [`policies/`](policies/) | YAML/JSON requirements + [`schema/policy.schema.json`](policies/schema/policy.schema.json) |
| [`factory/`](factory/) | Python `tf-factory` CLI, [`catalog.yaml`](factory/catalog.yaml), Jinja2 scaffolds |
| [`modules/azure/`](modules/azure/) | Shipped modules: `naming`, `private-endpoint`, `key-vault`, `storage` |
| [`modules/aws/`](modules/aws/), [`modules/gcp/`](modules/gcp/) | Stubs only in v1 |
| [`checkov/custom_checks/`](checkov/custom_checks/) | Custom checks mirroring policies |
| [`examples/`](examples/) | Composed consumer examples (local relative `source`) |
| [`pipelines/azure-devops/`](pipelines/azure-devops/) | CI: fmt, validate, Checkov, TFE publish guidance |
| [`.checkov.yaml`](.checkov.yaml) | Checkov config + intentional skips |

## How to work

### Before changing modules

1. Read the relevant policy files under `policies/`.
2. Check whether a catalog module already covers the need: `tf-factory list-modules`.
3. Prefer scaffolding over hand-rolling empty modules.

### Scaffold a new module

```bash
cd factory && python3 -m pip install -e . && cd ..
tf-factory validate-policy --policies ./policies
tf-factory scaffold --cloud azure --name <module> --from-policy ./policies
```

Then:

1. Implement resources in `modules/azure/<module>/main.tf`.
2. Keep `public_network_access_enabled` tied to `allow_public_network_access` (default false).
3. Compose `../private-endpoint` (or catalog ref) for data-plane access.
4. Register the module in [`factory/catalog.yaml`](factory/catalog.yaml) (local path + TFE name/provider/version).
5. Add or update an example under `examples/` if consumers need a composition pattern.
6. Add/adjust Checkov custom checks when you add a new policy rule.

### Change an existing Azure module

- Preserve private-by-default and tag validation.
- If you add a resource type covered by `security.baseline.yaml` / `networking.private.yaml`, satisfy those rules in code **and** Checkov.
- Update the module README with the secure baseline table when defaults change.
- Keep `versions.tf` on `azurerm ~> 3.100` unless you are deliberately bumping the whole catalog.

### Policy / Checkov changes

- New policy files must validate: `tf-factory validate-policy --policies ./policies`.
- Custom Checkov check IDs use the prefix `CKV2_TFFACTORY_AZURE_*`.
- Only add entries to `.checkov.yaml` `skip-check` with a short comment explaining why (org-specific CMK, variable-driven attributes Checkov cannot evaluate, etc.).

### Multi-cloud

- Do not invent full AWS/GCP modules unless asked.
- New clouds need templates under `factory/templates/<cloud>/module/` and `cloud:` values in policies.
- Shared concepts (private connectivity, naming, tags) stay in policy; provider bodies differ.

## Verification (run before finishing)

```bash
# Policy pack
tf-factory validate-policy --policies ./policies

# Unit tests (factory)
cd factory && python3 -m pip install -e ".[dev]" && pytest -q && cd ..

# Terraform
terraform fmt -check -recursive modules examples
for d in modules/azure/*/; do (cd "$d" && terraform init -backend=false -input=false && terraform validate); done
for d in examples/*/; do (cd "$d" && terraform init -backend=false -input=false && terraform validate); done

# Checkov
checkov -d modules -d examples --config-file .checkov.yaml --framework terraform
```

CI mirror: [`pipelines/azure-devops/module-ci.yml`](pipelines/azure-devops/module-ci.yml).

## Module reference convention

| Context | `source` |
|---------|----------|
| Local / examples | Relative path, e.g. `../../modules/azure/storage` |
| TFE / HCP Terraform | `app.terraform.io/<org>/<name>/azure` from `factory/catalog.yaml` |

Scaffold with `--use-tfe` only when emitting registry sources. Replace `<org>` in `catalog.yaml` before publishing.

## Do not

- Default any PaaS module to `public_network_access_enabled = true`.
- Treat VNet/IP ACLs as sufficient exposure control.
- Commit `.terraform/`, state files, lockfiles from one-off validates if gitignored, or real secrets.
- Hand-edit the plan file in agent sessions when one exists; follow the user’s plan/process instead.
- Broaden scope into VNet/ACR/App Service/etc. unless requested — extend via `tf-factory scaffold` when asked.

## Quick orientation for a new agent turn

1. Skim this file and [`README.md`](README.md).
2. Identify whether the task is **policy**, **factory CLI**, **module**, **Checkov/CI**, or **example**.
3. Make the smallest change that preserves Private Link–first defaults.
4. Run the verification commands that apply to your change.
5. Update `catalog.yaml` and docs when adding a module consumers should discover.
