# azure/key-vault

Key Vault with public network access disabled, RBAC, soft delete, and composed Private Endpoint.

## Secure baseline

| Control | Default |
|---------|---------|
| `public_network_access_enabled` | `false` |
| `enable_rbac_authorization` | `true` |
| Soft delete retention | 90 days |
| Purge protection | `true` |
| Private Endpoint | created (`create_private_endpoint = true`) |
| Network ACLs | `Deny` default — defense-in-depth only |

Set `allow_public_network_access = true` only as an explicit break-glass; CI Checkov rules fail this pattern.
