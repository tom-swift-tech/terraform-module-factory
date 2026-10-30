output "id" {
  description = "Storage account resource id."
  value       = azurerm_storage_account.this.id
}

output "name" {
  description = "Storage account name."
  value       = azurerm_storage_account.this.name
}

output "primary_blob_endpoint" {
  description = "Primary blob endpoint."
  value       = azurerm_storage_account.this.primary_blob_endpoint
}

output "private_endpoint_ids" {
  description = "Map of subresource → Private Endpoint id."
  value       = { for k, m in module.private_endpoint : k => m.id }
}
