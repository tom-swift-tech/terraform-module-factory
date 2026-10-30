# OPA policies for HCP Terraform / TFE

Plan-time enforcement for workspaces that consume factory modules.

## Why OPA here

Checkov (with `evaluate-variables`) mainly proves **module defaults** are safe. Consumers can still pass `allow_public_network_access = true` at plan time. OPA (or Sentinel) on the **Terraform plan** is the enforcement point that matches a TFE workflow.

## Setup

1. Export policy data from YAML:

   ```bash
   tf-factory export-policy-data --policies ./policies
   ```

2. In HCP Terraform / TFE, create an **OPA policy set** (or run task) that includes:
   - `policies/opa/terraform_azure.rego`
   - `policies/opa/data/policy_pack.json` (as OPA data document `policy_pack`)

3. Attach the policy set to workspaces that apply Azure factory modules.

## Local check

```bash
# after terraform plan -out=tfplan && terraform show -json tfplan > plan.json
opa eval -i plan.json -d policies/opa/data/policy_pack.json -d policies/opa/terraform_azure.rego 'data.terraform.azure.factory.deny'
```

## Sentinel

If your org standardizes on Sentinel instead of OPA, mirror the same rules in a Sentinel policy set. The YAML pack remains source of truth; regenerate/export before changing enforcement code.
