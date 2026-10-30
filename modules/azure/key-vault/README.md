# azure/key-vault

Key Vault with public network access disabled, RBAC, soft delete, and composed Private Endpoint.

Requires **azurerm ~> 4.0** (`rbac_authorization_enabled`).

## Secure baseline

| Control | Default |
|---------|---------|
| `public_network_access_enabled` | `false` |
| `rbac_authorization_enabled` | `true` |
| Soft delete retention | 90 days |
| Purge protection | on unless `tags.Environment == "dev"` (overridable) |
| Private Endpoint | created (`create_private_endpoint = true`) |
| Network ACLs | `Deny` — defense-in-depth only |

Plan-time denial of public access belongs in OPA/TFE ([`policies/opa/`](../../../policies/opa/)).
