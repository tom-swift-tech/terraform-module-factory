"""CKV2_TFFACTORY_AZURE_5: Prefer modules that compose private endpoints.

Graph/module-source awareness is limited in Checkov resource checks, so this
check flags storage/key vault configurations that enable public access — the
inverse of the Private Link requirement in policies/networking.private.yaml.
"""

from __future__ import annotations

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class RequirePrivateConnectivity(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure PaaS resources do not use public access instead of Private Link"
        id = "CKV2_TFFACTORY_AZURE_5"
        supported_resources = ("azurerm_storage_account", "azurerm_key_vault")
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict) -> CheckResult:
        value = conf.get("public_network_access_enabled")
        if value is None:
            return CheckResult.FAILED
        enabled = value[0] if isinstance(value, list) else value
        if enabled is True or enabled == "true":
            return CheckResult.FAILED
        return CheckResult.PASSED


check = RequirePrivateConnectivity()
