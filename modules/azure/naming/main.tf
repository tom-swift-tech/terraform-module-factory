/**
 * Policy-aligned Azure naming helpers.
 *
 * Defaults mirror policies/naming.example.yaml. Pass resource_prefixes /
 * region_codes overrides when you replace the example naming policy.
 */

locals {
  region_code = lookup(var.region_codes, var.region, replace(var.region, "/[^a-z0-9]/", ""))

  # Generic hyphenated pattern: {prefix}-{workload}-{env}-{region}-{suffix}
  hyphenated = {
    for type, prefix in var.resource_prefixes :
    type => lower("${prefix}-${var.workload}-${var.environment}-${local.region_code}-${var.suffix}")
    if type != "storage_account"
  }

  # Storage accounts: 3-24 chars, lowercase alphanumeric only
  storage_raw = lower(replace(
    "${var.resource_prefixes["storage_account"]}${var.workload}${var.environment}${local.region_code}${var.suffix}",
    "/[^a-z0-9]/",
    ""
  ))

  storage_account = substr(
    local.storage_raw,
    0,
    min(length(local.storage_raw), 24)
  )

  # Key Vault: 3-24, alphanumeric and hyphens
  key_vault_raw = lower("${var.resource_prefixes["key_vault"]}-${var.workload}-${var.environment}-${local.region_code}-${var.suffix}")
  key_vault     = substr(local.key_vault_raw, 0, min(length(local.key_vault_raw), 24))

  names = merge(local.hyphenated, {
    storage_account  = local.storage_account
    key_vault        = local.key_vault
    private_endpoint = lower("${var.resource_prefixes["private_endpoint"]}-${var.workload}-${var.environment}-${local.region_code}-${var.suffix}")
  })
}
