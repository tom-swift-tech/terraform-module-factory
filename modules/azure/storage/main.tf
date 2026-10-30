/**
 * Azure Storage Account — private-by-default baseline.
 *
 * - public_network_access_enabled defaults to false
 * - allow_nested_items_to_be_public = false
 * - min_tls_version = TLS1_2
 * - https_traffic_only_enabled = true
 * - Composes azure/private-endpoint for configured subresources
 * - Network ACLs default Deny — defense-in-depth only
 */

locals {
  public_network_access_enabled = var.allow_public_network_access
  pe_prefix                     = coalesce(var.private_endpoint_name_prefix, var.name)

  dns_by_subresource = {
    blob  = try(var.private_dns_zone_ids.blob, [])
    file  = try(var.private_dns_zone_ids.file, [])
    queue = try(var.private_dns_zone_ids.queue, [])
    table = try(var.private_dns_zone_ids.table, [])
    dfs   = try(var.private_dns_zone_ids.dfs, [])
  }
}

# checkov:skip=CKV_AZURE_206: replication type is variable-driven; validation forbids LRS (ZRS+)
resource "azurerm_storage_account" "this" {
  name                            = var.name
  resource_group_name             = var.resource_group_name
  location                        = var.location
  account_tier                    = var.account_tier
  account_replication_type        = var.account_replication_type
  account_kind                    = var.account_kind
  min_tls_version                 = "TLS1_2"
  https_traffic_only_enabled      = true
  allow_nested_items_to_be_public = false
  public_network_access_enabled   = local.public_network_access_enabled
  shared_access_key_enabled       = var.shared_access_key_enabled
  default_to_oauth_authentication = true
  tags                            = var.tags

  sas_policy {
    expiration_period = var.sas_expiration_period
    expiration_action = "Log"
  }

  network_rules {
    default_action             = "Deny"
    bypass                     = var.network_acl_bypass
    ip_rules                   = var.network_acl_ip_rules
    virtual_network_subnet_ids = var.network_acl_subnet_ids
  }

  blob_properties {
    versioning_enabled = true

    delete_retention_policy {
      days = 7
    }

    container_delete_retention_policy {
      days = 7
    }
  }
}

module "private_endpoint" {
  source   = "../private-endpoint"
  for_each = var.create_private_endpoint ? toset(var.private_endpoint_subresources) : toset([])

  name                           = "${local.pe_prefix}-${each.value}-pe"
  resource_group_name            = var.resource_group_name
  location                       = var.location
  subnet_id                      = var.private_endpoint_subnet_id
  private_connection_resource_id = azurerm_storage_account.this.id
  subresource_names              = [each.value]
  private_dns_zone_ids           = lookup(local.dns_by_subresource, each.value, [])
  tags                           = var.tags
}

check "private_endpoint_subnet_required" {
  assert {
    condition     = !var.create_private_endpoint || (var.private_endpoint_subnet_id != null && var.private_endpoint_subnet_id != "")
    error_message = "private_endpoint_subnet_id is required when create_private_endpoint is true."
  }
}
