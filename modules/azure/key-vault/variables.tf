variable "name" {
  type        = string
  description = "Key Vault name (prefer module.naming.key_vault)."
}

variable "resource_group_name" {
  type        = string
  description = "Resource group name."
}

variable "location" {
  type        = string
  description = "Azure region."
}

variable "tenant_id" {
  type        = string
  description = "Azure AD tenant id for the Key Vault."
}

variable "sku_name" {
  type        = string
  description = "Key Vault SKU."
  default     = "standard"
}

variable "soft_delete_retention_days" {
  type        = number
  description = "Soft delete retention in days."
  default     = 90
}

variable "purge_protection_enabled" {
  type        = bool
  description = "Enable purge protection (recommended outside short-lived sandboxes)."
  default     = true
}

variable "allow_public_network_access" {
  type        = bool
  description = "BREAK-GLASS only. Platform baseline requires Private Link; leave false."
  default     = false
}

variable "network_acl_bypass" {
  type        = string
  description = "Network ACL bypass (AzureServices or None). Defense-in-depth only."
  default     = "AzureServices"
}

variable "network_acl_ip_rules" {
  type        = list(string)
  description = "Optional IP rules. Not a substitute for Private Link."
  default     = []
}

variable "network_acl_subnet_ids" {
  type        = list(string)
  description = "Optional VNet subnet ids for service endpoints. Defense-in-depth only."
  default     = []
}

variable "private_endpoint_subnet_id" {
  type        = string
  description = "Subnet id for the Key Vault Private Endpoint. Required unless create_private_endpoint is false."
  default     = null
}

variable "private_dns_zone_ids" {
  type        = list(string)
  description = "Private DNS zone ids for privatelink.vaultcore.azure.net."
  default     = []
}

variable "create_private_endpoint" {
  type        = bool
  description = "Create a composed Private Endpoint (required by platform networking policy)."
  default     = true
}

variable "private_endpoint_name" {
  type        = string
  description = "Optional Private Endpoint name override."
  default     = null
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
