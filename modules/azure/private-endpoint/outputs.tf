output "id" {
  description = "Private Endpoint resource id."
  value       = azurerm_private_endpoint.this.id
}

output "name" {
  description = "Private Endpoint name."
  value       = azurerm_private_endpoint.this.name
}

output "private_service_connection_name" {
  description = "Private service connection name."
  value       = "${var.name}-psc"
}

output "network_interface_id" {
  description = "NIC id attached to the Private Endpoint."
  value       = try(azurerm_private_endpoint.this.network_interface[0].id, null)
}

output "private_ip_address" {
  description = "Primary private IP of the endpoint (when available)."
  value = try(
    azurerm_private_endpoint.this.private_service_connection[0].private_ip_address,
    null
  )
}
