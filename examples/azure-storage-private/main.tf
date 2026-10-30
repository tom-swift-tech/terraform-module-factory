/**
 * Composed example: naming + storage + private endpoint (via storage module).
 *
 * Uses relative local sources for development. For TFE, switch sources to the
 * registry addresses in factory/catalog.yaml.
 */

module "naming" {
  source = "../../modules/azure/naming"

  workload    = var.workload
  environment = var.environment
  region      = var.location
  suffix      = "01"
}

module "storage" {
  source = "../../modules/azure/storage"

  name                = module.naming.storage_account
  resource_group_name = var.resource_group_name
  location            = var.location
  tags                = var.tags

  allow_public_network_access   = false
  create_private_endpoint       = true
  private_endpoint_subnet_id    = var.private_endpoint_subnet_id
  private_endpoint_subresources = ["blob"]
  private_dns_zone_ids = {
    blob = [var.blob_private_dns_zone_id]
  }

  network_acl_bypass = ["AzureServices"]
}
