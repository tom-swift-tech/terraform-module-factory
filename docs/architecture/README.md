# Architecture diagrams — Private Link baseline

Visio-style diagrams for **application teams** and **ISO** (Information Security).

## Primary diagram

| File | Use |
|------|-----|
| [`private-link-baseline.svg`](private-link-baseline.svg) | Infrastructure design + data flow (print / Confluence / Visio import) |

**Open:** double-click the SVG, or drag into Visio / PowerPoint / draw.io.

**Export PNG (optional):**

```bash
# if rsvg-convert or inkscape is available
rsvg-convert -w 2400 docs/architecture/private-link-baseline.svg -o docs/architecture/private-link-baseline.png
```

## What the diagram shows

### Infrastructure (left → right)

1. **Untrusted / Internet** — public clients and public PaaS endpoints (baseline: disabled).
2. **App / corporate network** — workloads, private CI runners, Private DNS.
3. **Private connectivity zone** — dedicated PE subnet, Private Endpoint, Private DNS zone group (`azure/private-endpoint`).
4. **Azure PaaS (locked)** — Storage and Key Vault with `public_network_access_enabled = false`, Deny ACLs as defense-in-depth.

### Data flow

| Path | Result |
|------|--------|
| App / runner → PE subnet → Private Endpoint → PaaS | **Allowed** (private data plane) |
| Internet → public PaaS endpoint | **Denied** (module default + OPA at plan time) |
| Relying on IP/VNet ACLs with public access on | **Denied** (policy: ACLs are not primary) |

### Governance band (bottom)

Policy pack → `tf-factory` → module catalog → Azure DevOps CI → TFE/HCP registry → **OPA on plan**.

## For application teams

- Consume modules from the TFE private registry (`…/azurerm`), not by copying HCL.
- Provide PE subnet + Private DNS zone IDs; keep `allow_public_network_access = false`.
- Apply required tags: `Environment`, `Owner`, `CostCenter`, `DataClassification`.
- Run Terraform from a network path that can resolve and reach Private Endpoints (self-hosted agents / private runners).
- Set provider `storage_use_azuread = true` when shared keys are disabled (factory default).

## For ISO

| Control | Where enforced |
|---------|----------------|
| No public network access on Storage / Key Vault | Module defaults + OPA (`policies/opa/`) + Checkov CI |
| Private Link required; ACLs not sufficient alone | `policies/networking.private.yaml` → OPA |
| TLS 1.2+, no public blobs, KV RBAC | Security baseline + OPA / Checkov |
| Required tags + value patterns | `tags.required.yaml` → OPA |
| Loud break-glass | `allow_public_network_access` (default false); OPA denies `true` |
| Naming / collision safety | Generated `azure/naming` (suffix preserved) |

**Evidence pack:** this diagram + policy YAML + OPA policy set attachment on TFE workspaces + ADO Checkov results.

## Related docs

- [AGENTS.md](../../AGENTS.md) — agent / platform engineer rules
- [TFE publishing](../TFE_PUBLISHING.md) — monorepo VCS modules
- [OPA README](../../policies/opa/README.md) — plan-time enforcement setup
