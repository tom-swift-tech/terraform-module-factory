variable "workload" {
  type    = string
  default = "demo"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "location" {
  type    = string
  default = "eastus"
}

variable "resource_group_name" {
  type        = string
  description = "Existing resource group for the example."
  default     = "rg-tf-factory-demo"
}

variable "private_endpoint_subnet_id" {
  type        = string
  description = "Subnet id that will host the storage Private Endpoint."
  default     = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-tf-factory-demo/providers/Microsoft.Network/virtualNetworks/vnet-demo/subnets/snet-pe"
}

variable "blob_private_dns_zone_id" {
  type        = string
  description = "Private DNS zone id for privatelink.blob.core.windows.net."
  default     = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-tf-factory-demo/providers/Microsoft.Network/privateDnsZones/privatelink.blob.core.windows.net"
}

variable "tags" {
  type = map(string)
  default = {
    Environment        = "dev"
    Owner              = "platform-engineering"
    CostCenter         = "shared-platform"
    DataClassification = "internal"
  }
}
