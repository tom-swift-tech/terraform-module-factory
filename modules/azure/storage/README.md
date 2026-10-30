# azure/storage

Storage Account locked down for Private Link with defense-in-depth network ACLs.

## Secure baseline

| Control | Default |
|---------|---------|
| `public_network_access_enabled` | `false` |
| `allow_nested_items_to_be_public` | `false` |
| `min_tls_version` | `TLS1_2` |
| HTTPS only | `true` |
| Network rules default action | `Deny` |
| Private Endpoint | `blob` (configurable) |

Public access requires the explicit break-glass variable `allow_public_network_access = true`, which custom Checkov rules fail in CI.
