# azure/naming

Pure naming helpers aligned to `policies/naming.example.yaml`. No cloud resources.

## Usage

```hcl
module "naming" {
  source      = "../../modules/azure/naming"
  workload    = "payments"
  environment = "prod"
  region      = "eastus"
  suffix      = "01"
}

# module.naming.storage_account → stpaymentseuseus01 (trimmed to constraints)
# module.naming.key_vault       → kv-payments-prod-eus-01
```

Replace prefixes/region codes via variables when you drop in your real naming standards.
