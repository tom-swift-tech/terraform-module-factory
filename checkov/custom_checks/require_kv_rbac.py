"""CKV2_TFFACTORY_AZURE_4: Require Key Vault RBAC authorization."""

from __future__ import annotations

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class RequireKeyVaultRbac(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Key Vault uses Azure RBAC authorization"
        id = "CKV2_TFFACTORY_AZURE_4"
        supported_resources = ("azurerm_key_vault",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict) -> CheckResult:
        # azurerm 4.x renamed enable_rbac_authorization -> rbac_authorization_enabled
        for key in ("rbac_authorization_enabled", "enable_rbac_authorization"):
            value = conf.get(key)
            if value is None:
                continue
            enabled = value[0] if isinstance(value, list) else value
            if enabled is True or enabled == "true":
                return CheckResult.PASSED
            return CheckResult.FAILED
        return CheckResult.FAILED


check = RequireKeyVaultRbac()
