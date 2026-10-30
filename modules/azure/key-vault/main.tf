/**
 * Azure Key Vault — private-by-default baseline.
 *
 * - public_network_access_enabled defaults to false
 * - RBAC authorization enabled (azurerm 4.x: rbac_authorization_enabled)
 * - Soft delete always on; purge protection required outside Environment=dev (policy)
 * - Composes azure/private-endpoint for vault access
 * - Network ACLs are defense-in-depth only
 */

locals {
  public_network_access_enabled = var.allow_public_network_access
  private_endpoint_name         = coalesce(var.private_endpoint_name, "${var.name}-pe")

  # policies/security.baseline.yaml: purge protection required outside dev
  environment_tag = try(var.tags["Environment"], "")
  purge_protection_enabled = (
    var.purge_protection_enabled != null
    ? var.purge_protection_enabled
    : local.environment_tag != "dev"
  )

  # Always Deny — public access is controlled by public_network_access_enabled
  network_default_action = "Deny"
}

resource "azurerm_key_vault" "this" {
  name                          = var.name
  location                      = var.location
  resource_group_name           = var.resource_group_name
  tenant_id                     = var.tenant_id
  sku_name                      = var.sku_name
  soft_delete_retention_days    = var.soft_delete_retention_days
  purge_protection_enabled      = local.purge_protection_enabled
  rbac_authorization_enabled    = true
  public_network_access_enabled = local.public_network_access_enabled
  tags                          = var.tags

  network_acls {
    bypass                     = var.network_acl_bypass
    default_action             = local.network_default_action
    ip_rules                   = var.network_acl_ip_rules
    virtual_network_subnet_ids = var.network_acl_subnet_ids
  }
}

module "private_endpoint" {
  source = "../private-endpoint"
  count  = var.create_private_endpoint ? 1 : 0

  name                           = local.private_endpoint_name
  resource_group_name            = var.resource_group_name
  location                       = var.location
  subnet_id                      = var.private_endpoint_subnet_id
  private_connection_resource_id = azurerm_key_vault.this.id
  subresource_names              = ["vault"]
  private_dns_zone_ids           = var.private_dns_zone_ids
  tags                           = var.tags
}

check "private_endpoint_subnet_required" {
  assert {
    condition     = !var.create_private_endpoint || (var.private_endpoint_subnet_id != null && var.private_endpoint_subnet_id != "")
    error_message = "private_endpoint_subnet_id is required when create_private_endpoint is true."
  }
}
