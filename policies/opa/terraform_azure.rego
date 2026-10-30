# TFE / HCP Terraform plan-time enforcement (OPA).
# Attach this policy set to workspaces that consume factory modules.
# Data file: policies/opa/data/policy_pack.json (tf-factory export-policy-data)
#
# Input: Terraform plan JSON (terraform show -json) or TFE run task / OPA integration payload.
# Expected shape used here: input.resource_changes[].type / .change.after

package terraform.azure.factory

import future.keywords.contains
import future.keywords.if
import future.keywords.in

# Fallback defaults if data.policy_pack is not loaded
default required_tags := ["Environment", "Owner", "CostCenter", "DataClassification"]

required_tags := data.policy_pack.required_tags if {
	data.policy_pack.required_tags
}

tag_patterns := object.get(data.policy_pack, "tag_value_patterns", {})

attribute_rules := object.get(data.policy_pack, "attribute_rules", [])

deny contains msg if {
	some change in input.resource_changes
	change.type in {"azurerm_storage_account", "azurerm_key_vault"}
	after := object.get(change.change, "after", {})
	after.public_network_access_enabled == true
	msg := sprintf("%s %s: public_network_access_enabled must be false (Private Link required; ACLs are not enough)", [change.type, change.address])
}

deny contains msg if {
	some change in input.resource_changes
	change.type == "azurerm_storage_account"
	after := object.get(change.change, "after", {})
	after.min_tls_version != "TLS1_2"
	after.min_tls_version != "TLS1_3"
	msg := sprintf("%s: min_tls_version must be TLS1_2 or TLS1_3", [change.address])
}

deny contains msg if {
	some change in input.resource_changes
	change.type == "azurerm_storage_account"
	after := object.get(change.change, "after", {})
	after.allow_nested_items_to_be_public == true
	msg := sprintf("%s: allow_nested_items_to_be_public must be false", [change.address])
}

deny contains msg if {
	some change in input.resource_changes
	change.type == "azurerm_key_vault"
	after := object.get(change.change, "after", {})
	# azurerm 4.x
	rbac := object.get(after, "rbac_authorization_enabled", object.get(after, "enable_rbac_authorization", false))
	rbac != true
	msg := sprintf("%s: Key Vault must use RBAC authorization", [change.address])
}

deny contains msg if {
	some change in input.resource_changes
	tags := object.get(object.get(change.change, "after", {}), "tags", {})
	tags != null
	some tag in required_tags
	not tags[tag]
	msg := sprintf("%s: missing required tag %s", [change.address, tag])
}

deny contains msg if {
	some change in input.resource_changes
	tags := object.get(object.get(change.change, "after", {}), "tags", {})
	tags != null
	some key, pattern in tag_patterns
	value := tags[key]
	not regex.match(pattern, value)
	msg := sprintf("%s: tag %s=%q does not match %s", [change.address, key, value, pattern])
}

# Generic require/deny attribute rules exported from the YAML policy pack
deny contains msg if {
	some rule in attribute_rules
	rule.severity == "error"
	some change in input.resource_changes
	change.type == rule.resource_type
	after := object.get(change.change, "after", {})
	rule.op == "eq"
	object.get(after, rule.attribute, null) != rule.value
	msg := sprintf("%s: policy %s requires %s == %v", [change.address, rule.id, rule.attribute, rule.value])
}

deny contains msg if {
	some rule in attribute_rules
	rule.severity == "error"
	some change in input.resource_changes
	change.type == rule.resource_type
	after := object.get(change.change, "after", {})
	rule.op == "deny_eq"
	object.get(after, rule.attribute, null) == rule.value
	msg := sprintf("%s: policy %s denies %s == %v", [change.address, rule.id, rule.attribute, rule.value])
}
