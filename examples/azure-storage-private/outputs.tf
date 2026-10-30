output "storage_account_name" {
  description = "Rendered storage account name from naming module."
  value       = module.storage.name
}

output "storage_account_id" {
  description = "Storage account resource id."
  value       = module.storage.id
}

output "private_endpoint_ids" {
  description = "Private Endpoint ids created for storage subresources."
  value       = module.storage.private_endpoint_ids
}

output "naming_map" {
  description = "Full naming map for the workload."
  value       = module.naming.names
}
