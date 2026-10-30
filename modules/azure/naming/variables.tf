variable "workload" {
  type        = string
  description = "Short workload or application identifier (no spaces)."
}

variable "environment" {
  type        = string
  description = "Environment code (dev|test|staging|prod)."

  validation {
    condition     = contains(["dev", "test", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, test, staging, prod."
  }
}

variable "region" {
  type        = string
  description = "Azure region name (e.g. eastus). Mapped to a short code internally."
}

variable "suffix" {
  type        = string
  description = "Numeric or short disambiguator."
  default     = "01"
}

variable "resource_prefixes" {
  type        = map(string)
  description = "Optional override of resource type prefixes (defaults mirror policies/naming.example.yaml)."
  default = {
    resource_group          = "rg"
    storage_account         = "st"
    key_vault               = "kv"
    private_endpoint        = "pe"
    virtual_network         = "vnet"
    subnet                  = "snet"
    network_security_group  = "nsg"
    log_analytics_workspace = "log"
    application_insights    = "appi"
  }
}

variable "region_codes" {
  type        = map(string)
  description = "Optional override of Azure region → short code mapping."
  default = {
    eastus      = "eus"
    eastus2     = "eus2"
    westus2     = "wus2"
    westeurope  = "weu"
    northeurope = "neu"
  }
}
