# azure/private-endpoint

Creates an Azure Private Endpoint and optional Private DNS zone group.

## Usage

```hcl
module "pe" {
  source                         = "../../modules/azure/private-endpoint"
  name                           = module.naming.private_endpoint
  resource_group_name            = var.resource_group_name
  location                       = var.location
  subnet_id                      = var.private_endpoint_subnet_id
  private_connection_resource_id = module.storage.id
  subresource_names              = ["blob"]
  private_dns_zone_ids           = [var.blob_private_dns_zone_id]
  tags                           = var.tags
}
```
