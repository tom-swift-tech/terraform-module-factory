output "id" {
  description = "Key Vault resource id."
  value       = azurerm_key_vault.this.id
}

output "name" {
  description = "Key Vault name."
  value       = azurerm_key_vault.this.name
}

output "uri" {
  description = "Key Vault URI."
  value       = azurerm_key_vault.this.vault_uri
}

output "private_endpoint_id" {
  description = "Composed Private Endpoint id (if created)."
  value       = try(module.private_endpoint[0].id, null)
}
