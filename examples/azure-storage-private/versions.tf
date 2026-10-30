terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
  # Required when modules set shared_access_key_enabled = false (default).
  # Without this, the provider reads queue/table properties over the data plane with
  # shared keys and receives 403 once public network access is disabled.
  storage_use_azuread = true
  # Example only — authenticate via Azure CLI / OIDC / service principal in real runs.
  # Applying with Private Link also requires the runner to reach the PE (private network / VPN / self-hosted agent).
}
