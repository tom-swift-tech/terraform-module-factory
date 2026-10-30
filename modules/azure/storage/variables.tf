variable "name" {
  type        = string
  description = "Storage account name (prefer module.naming.storage_account)."

  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.name))
    error_message = "Storage account name must be 3-24 lowercase alphanumeric characters."
  }
}

variable "resource_group_name" {
  type        = string
  description = "Resource group name."
}

variable "location" {
  type        = string
  description = "Azure region."
}

variable "account_tier" {
  type        = string
  description = "Storage account tier."
  default     = "Standard"
}

variable "account_replication_type" {
  type        = string
  description = "Replication type (LRS, ZRS, GRS, RAGRS, GZRS, RAGZRS). Prefer ZRS or better."
  default     = "ZRS"

  validation {
    condition     = contains(["ZRS", "GRS", "RAGRS", "GZRS", "RAGZRS"], var.account_replication_type)
    error_message = "account_replication_type must be ZRS or geo/zone redundant (LRS is not permitted by baseline)."
  }
}

variable "shared_access_key_enabled" {
  type        = bool
  description = "Allow shared key auth. Prefer Azure AD; default false."
  default     = false
}

variable "sas_expiration_period" {
  type        = string
  description = "SAS expiration period (ISO-8601 duration) when shared key/SAS is used."
  default     = "00.01:00:00"
}

variable "account_kind" {
  type        = string
  description = "Storage account kind."
  default     = "StorageV2"
}

variable "allow_public_network_access" {
  type        = bool
  description = "BREAK-GLASS only. Platform baseline requires Private Link; leave false."
  default     = false
}

variable "network_acl_bypass" {
  type        = list(string)
  description = "Network rules bypass values. Defense-in-depth only."
  default     = ["AzureServices"]
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
  description = "Subnet id for Private Endpoints. Required when create_private_endpoint is true."
  default     = null
}

variable "private_dns_zone_ids" {
  type = object({
    blob  = optional(list(string), [])
    file  = optional(list(string), [])
    queue = optional(list(string), [])
    table = optional(list(string), [])
    dfs   = optional(list(string), [])
  })
  description = "Private DNS zone ids keyed by subresource."
  default     = {}
}

variable "private_endpoint_subresources" {
  type        = list(string)
  description = "Private Link subresources to create endpoints for."
  default     = ["blob"]
}

variable "create_private_endpoint" {
  type        = bool
  description = "Create composed Private Endpoints (required by platform networking policy)."
  default     = true
}

variable "private_endpoint_name_prefix" {
  type        = string
  description = "Prefix for Private Endpoint names. Defaults to the storage account name."
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
