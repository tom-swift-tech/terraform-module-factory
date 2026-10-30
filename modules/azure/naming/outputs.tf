output "region_code" {
  description = "Resolved short region code."
  value       = local.region_code
}

output "names" {
  description = "Map of resource_type → rendered name."
  value       = local.names
}

output "resource_group" {
  description = "Resource group name."
  value       = local.names["resource_group"]
}

output "storage_account" {
  description = "Storage account name (no hyphens, max 24)."
  value       = local.names["storage_account"]
}

output "key_vault" {
  description = "Key Vault name."
  value       = local.names["key_vault"]
}

output "private_endpoint" {
  description = "Private Endpoint name."
  value       = local.names["private_endpoint"]
}
