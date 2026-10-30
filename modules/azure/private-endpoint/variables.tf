variable "name" {
  type        = string
  description = "Private Endpoint name (prefer module.naming.private_endpoint)."
}

variable "resource_group_name" {
  type        = string
  description = "Resource group for the Private Endpoint."
}

variable "location" {
  type        = string
  description = "Azure region."
}

variable "subnet_id" {
  type        = string
  description = "Subnet id that hosts the Private Endpoint (no subnet delegation)."
}

variable "private_connection_resource_id" {
  type        = string
  description = "Target PaaS resource id (storage account, key vault, etc.)."
}

variable "subresource_names" {
  type        = list(string)
  description = "Private Link subresource names (e.g. [\"blob\"], [\"vault\"])."
}

variable "private_dns_zone_ids" {
  type        = list(string)
  description = "Private DNS zone ids. Empty skips the DNS zone group."
  default     = []
}

variable "private_dns_zone_group_name" {
  type        = string
  description = "Name of the Private DNS zone group."
  default     = "default"
}

variable "tags" {
  type        = map(string)
  description = "Resource tags. Must include Environment, Owner, CostCenter, DataClassification."
  default     = {}

  validation {
    condition = alltrue([
      contains(keys(var.tags), "Environment"),
      contains(keys(var.tags), "Owner"),
      contains(keys(var.tags), "CostCenter"),
      contains(keys(var.tags), "DataClassification"),
    ])
    error_message = "tags must include Environment, Owner, CostCenter, DataClassification."
  }
}
